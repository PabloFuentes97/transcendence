import { pages } from "../controllers/index.js"
import { startBackgroundTransition } from "../js/background.js";
import * as gameSocket from "../js/gameSocket.js";

const router = async () =>
{
	try{
		gameSocket.idle();
		switch (location.hash)
		{
			case "#login":
				await pages.login();
				break;
			case "#home":
				await pages.home();
				break;
			case "#profile":
				await pages.profile();
				break;
			case "#play":
				await pages.play();
				break;
			case "#social":
				await pages.social();
				break;
			case "#settings":
				await pages.settings();
				break;
			case "#leaderboard":
				await pages.leaderboard();
				break;
			default:
				await pages.home();
				break;				
		}
		startBackgroundTransition();
	}
	catch (excepcion)
	{
		console.warn(excepcion);
	}
}

export { router };

//Ahora q lo pienso, se puede hacer tag individual tipo menu-link y pasar param a route y q así no se vea nunca nada en el url