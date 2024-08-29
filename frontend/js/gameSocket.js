
import loadGameView from '../controllers/game.controller.js'
import { changeToMatchMakingScreen, resetQueueState, setPlayersInTournamentQueue } from './playModeManager.js';
import * as tournamentManager from './tournamentManager.js';
import * as game from '../game/game.js'
import getMyUserInfo from './apisCallers/userInfo/getMyUserInfo.js';
import { startCountdown } from './countdown.js';
import { setPlayerNames, setScores } from './gameUITools.js';
import { setGameTime, stopMMTimer } from './counter.js';
import { loadEndMatchData } from './endMatchDataDisplay.js';
import showNotification from './showNotification.js';

export let gameSocket = null;

export function send(params){
	gameSocket.send(params);
}

export function createGameSocket(){
	gameSocket = new WebSocket(
		'wss://'
		+ window.location.host
		+ '/ws/game/?token='
		+ localStorage.getItem('jwtToken')
	);

	gameSocket.onclose = function(e) {
		console.error('Game socket closed unexpectedly');
	};
	idle();
}

export function closeGameSocket(){
	gameSocket.send(JSON.stringify({
		"type": "log_out"}));
	gameSocket.onclose = function () {};
	gameSocket.onmessage = function () {};
	gameSocket.close();
	gameSocket = null;
}

export function updateAlias(alias){
	gameSocket.send(JSON.stringify({
		"type": "update_alias",
		"alias": alias
	}))
}

export function idle(){
	leaveGame();
	if (gameSocket)
		gameSocket.onmessage = function () {};
	inTournament = false;
	inGame = false;
}

export function localMode(){
	if (!gameSocket)
		return;
	gameSocket.send(JSON.stringify({
		"type": "join",
		"mode": "local"
	}));
	gameSocket.onmessage = function(e){
		const data = JSON.parse(e.data);

		if (data.hasOwnProperty("type")){
			if (data["type"] == "join"){
				if (checkJoinStatus(data["status"], data["code"]))
					loadGameView();
			}
		}
	}
}

export async function onlineMode(){
	if (!gameSocket)
		return;
	
	const userData = await getMyUserInfo();
	
	gameSocket.send(JSON.stringify({
		"type": "join",
		"mode": "online",
		"name": userData.alias,
		"elo": userData.elo
	}));
	gameSocket.onmessage = function(e) {
		const data = JSON.parse(e.data);
		
		if (data.hasOwnProperty("type"))
		{
			if (data["type"] == "join"){
				if(checkJoinStatus(data["status"], data["code"]))
					changeToMatchMakingScreen("online");
			}
			if (data["type"] == "accept_matchmaking")
			{
				stopMMTimer();
				loadGameView();
				resetQueueState();
			}
		}
	};
}

export let inTournament = false;
export function tournamentMode(){
	if (!gameSocket)
		return;
	gameSocket.send(JSON.stringify({
		"type": "join",
		"mode": "tournament"
	}));
	gameSocket.onmessage = function(e) {
		const data = JSON.parse(e.data);
		
		if (data.hasOwnProperty("type"))
		{
			if (data["type"] == "join"){
				stopMMTimer();
				if(checkJoinStatus(data["status"], data["code"]))
					changeToMatchMakingScreen("tournament");
			}
			if (data["type"] == "init_tournament")
			{
				tournamentManager.clearTournament();
				for (let i = 0; i < 4; i++)
					tournamentManager.addInitialPlayer(data["players"][i], i);
				tournamentManager.loadTournamentBrackets();
				resetQueueState();
				inTournament = true;
			}
			else if (data["type"] == "tournament_players_queue"){
				setPlayersInTournamentQueue(data["players_n"]);
			}
			readTournamentMessage(data);
		}
	};
}

function checkJoinStatus(status, code){
	if (!gameSocket)
		return;
	if (status == "success")
		return true;
	else if (status == "error"){
		showNotification(code);
		gameSocket.onmessage = null;
		return false;
	}
}

export function tournamentBracketsMode(){
	if (!gameSocket)
		return;
	gameSocket.onmessage = function(e) {
		let data = JSON.parse(e.data);
        if (data.hasOwnProperty("type"))
        {
			if (data["type"] == "tournament_round_countdown"){
				tournamentManager.startBracketsCountdown();
			}
			else if (data["type"] == "tournament_round_begin"){
				loadGameView();
			}
			readTournamentMessage(data);
		}
	}
}

export function leaveQueue(queueType){
	if (!gameSocket)
		return;
	gameSocket.send(JSON.stringify({
		"type": "leave",
		"context": queueType
	}));
	gameSocket.onmessage = null;
}

let inGame = false;
let endedMatch = false;
export function listenGameUpdates(){
	if (!gameSocket)
		return;
	inGame = true;
	endedMatch = false;
	gameSocket.onmessage = function(e) {
        let data = JSON.parse(e.data);
        if (data.hasOwnProperty("type"))
        {
            if (data["type"] == "game_update")
            {
				game.updateGameData(data);
				setGameTime(data.state.Time);
				setScores(data.state.Score[0], data.state.Score[1]);
            }
            else if (data["type"] == "match_info")
            {
				game.setGameSizes(data.state);
                 startCountdown(data.state.duration); ///INICIA EL TIMER
                if (data.state.match_type != "local")
                    setPlayerNames(data.state.players_name[0], data.state.players_name[1]);
                else
                    setPlayerNames("Player 1", "Player 2");
            }
            else if (data["type"] == "ended_match")
            {
				endedMatch = true;
				game.setGameRunningToFalse();
				game.stopAnimation();
				if (data["mode"] == "tournament" && data.result.toLowerCase() == "defeat")
					inTournament = false;
				loadEndMatchData(data);
            }

			//Tournament data
			else 
				readTournamentMessage(data);
        }
    }
}

export function leaveGame(){
	if (!gameSocket)
		return;
	if (!inGame && !inTournament){
		return;
	}
	if (endedMatch){
		endedMatch = false;
		inGame = false;
		return;
	}
	let context = "match";
	if (inTournament)
		context = "tournament";
	gameSocket.send(JSON.stringify({
		"type": "leave",
		"context": context
	}));
	inGame = false;
	inTournament = false;

	idle();
}

function readTournamentMessage(data){
	if (data["type"] == "tournament_match_ended"){
		tournamentManager.addFinalistPlayer(data.winner, data.match_id);
	}
}