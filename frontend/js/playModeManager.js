
import * as gameSocket from '../js/gameSocket.js';
import { startMMTimer, stopMMTimer } from '../js/counter.js';
import { changeGameMode } from '../game/game.js';
import { getRandomMessage } from './getRandomMessage.js';

let inTournamentQueue = false;
let inQueue = false;
let playersInTournamentQueue = 0;

export function loadLocalMode(){
	gameSocket.localMode();
	changeGameMode("offline");
}

export function loadOnlineMode(){
    gameSocket.onlineMode();
	changeGameMode("online");
	inQueue = true;
}

export function loadTournamentMode(){
	gameSocket.tournamentMode();
	inTournamentQueue = true;
	changeGameMode("online");
}

export async function changeToMatchMakingScreen(mode){

	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	else
		content.innerHTML = "";

	const response = await fetch('../html/matchMakingScreen.html');
	content.innerHTML = await response.text();
	const playersNuberElement = document.getElementById("current-tournament-players");
	if (playersNuberElement)
		playersNuberElement.innerHTML = playersInTournamentQueue;
	getRandomMessage();
	startMMTimer();

	if (mode == "tournament"){
		const tournamentPlayersElement = document.getElementById("tournament-players");
		if (tournamentPlayersElement)
			tournamentPlayersElement.classList.remove("tc-invisible-text");
	}
}

export function setPlayersInTournamentQueue(number){
	playersInTournamentQueue = number;
	const playersNuberElement = document.getElementById("current-tournament-players");
	if (playersNuberElement)
		playersNuberElement.innerHTML = number;
}

export function leaveQueue(){
	let queueType = null;
	if (inQueue)
		queueType = "matchmaking";
	else if (inTournamentQueue)
		queueType = "tournament";

	if (queueType != null){
		gameSocket.leaveQueue(queueType);
		resetQueueState();
		stopMMTimer();
	}
}

export function resetQueueState(){
	inTournamentQueue = false;
	inQueue = false;
}