import Menu from './menu.controller.js'
import * as playModeManager from '../js/playModeManager.js'
import { isGameLoaded, stopAnimation } from '../game/game.js';
import { leaveGame } from '../js/gameSocket.js';

export default async() => {
	
	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	else
		content.innerHTML = "";

	const response = await fetch('../html/play.html');
	if (!response.ok)
		throw response.statusText;
	content.innerHTML = await response.text();
	setListeners();

	if (isGameLoaded())
		stopAnimation();
	playModeManager.leaveQueue();
};

function setListeners(){
	const localDiv = document.getElementById("play-mode-local");
	localDiv.addEventListener('click', playModeManager.loadLocalMode);

	const onlineDiv = document.getElementById("play-mode-online");
	onlineDiv.addEventListener('click', playModeManager.loadOnlineMode);

	const tournamentDiv = document.getElementById("play-mode-tournament");
	tournamentDiv.addEventListener('click', playModeManager.loadTournamentMode);
}
