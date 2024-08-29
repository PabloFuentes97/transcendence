import { router } from "./router/index.routes.js";
import { isGameLoaded, stopAnimation } from "./game/game.js";
import getMyUserInfo from "./js/apisCallers/userInfo/getMyUserInfo.js";
import showProfile from "./js/showProfile.js";

import { gameSocket, leaveGame } from "./js/gameSocket.js";
import { createGameSocket } from "./js/gameSocket.js";
import { leaveQueue } from "./js/playModeManager.js";
import { startBackgroundAnimation } from "./js/background.js";
import { connectLoginSocket } from "./js/login.js";

const navigateTo = url => {
	history.pushState(null, null, url);
	if (isGameLoaded()){
		stopAnimation();
	}
	startBackgroundAnimation();
	leaveQueue(); //leaveQueue from playModeManager
	leaveGame();
	router();
};

function handlePopstate(){
	isUserLogged();
	if (isGameLoaded()){
		stopAnimation();
	}
	startBackgroundAnimation();
	leaveGame();
	leaveQueue();
}

async function isUserLogged(){

	// router();
	// return;

	const jwtToken = localStorage.getItem('jwtToken');
	if (jwtToken){
		const result = (await getMyUserInfo());
		const isJwtValid = !((await result) == null);
		if (isJwtValid){
			if (gameSocket == null){
				createGameSocket();
				connectLoginSocket();
			}
			router();
		}
		else{
			localStorage.removeItem('jwtToken');
			navigateTo("#login");
		}
	}
	else{
		navigateTo("#login");
	}
}

window.addEventListener("popstate", handlePopstate);

document.addEventListener("DOMContentLoaded", () => {
	isUserLogged()
	document.addEventListener('click', e => {
		if (e.target.id == "profile-image")
			showProfile(e.target.getAttribute('alias'));
	})
});
