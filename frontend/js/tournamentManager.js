import { isGameLoaded } from "../game/game.js";
import *  as gameSocket from "./gameSocket.js";

let initialPlayers = [];
let finalistPlayers = [];
let winner = " ";

export async function loadTournamentBrackets(){
    gameSocket.tournamentBracketsMode();
    if (isGameLoaded())
        return;
	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	else
		content.innerHTML = "";

	let brackets = await getTournamentBracketsHtml();
    brackets = fillTournamentBrackets(brackets);
	content.innerHTML = await brackets;

    drawLines();
    if (winner != " " && winner != undefined)
        displayWinner();
    window.addEventListener('resize', drawLines);
}

async function getTournamentBracketsHtml(){
    
	const response = await fetch('../html/tournamentBrackets.html');
	if (!response.ok)
		throw response.statusText;

	return (await response.text());
}

async function fillTournamentBrackets(brackets){
    for (let i = 0; i < 4; i++){
        brackets = brackets.replace(`\${position${i}}`, initialPlayers[i]);
        const finalistPostion = Math.floor(i / 2);
        if (finalistPlayers[finalistPostion]){
            if (finalistPlayers[finalistPostion] != initialPlayers[i] && finalistPlayers[finalistPostion] != " "){
                brackets = brackets.replace(`\${result${i}}`, 'tc-tournament-defeat')
            }
            else{
                brackets = brackets.replace(`\${result${i}}`, '')
            }
        }
    }

    for (let i = 0; i < 2; i++){
        const player = finalistPlayers[i];
        brackets = brackets.replace(`\${finalist${i}}`, player);
        if (winner != " " && winner != player && winner != undefined){
            brackets = brackets.replace(`\${result${i + 4}}`, 'tc-tournament-defeat');
        }
        else{
            brackets = brackets.replace(`\${result${i + 4}}`, '');
        }
    }

    brackets = brackets.replace('${winner}', winner);

    return brackets;
}

export function clearTournament(){
    for (let i = 0; i < 4; i++)
        initialPlayers[i] = ' ';
    for (let i = 0; i < 3; i++)
        finalistPlayers[i] = ' '
    winner = " ";
}

export function addInitialPlayer(player, position){
    initialPlayers[position] = player;
}

export function addFinalistPlayer(player, position){
    if (position == 2){
        winner = player;
    }
    else{
        const countDownDiv = document.getElementById("tournamentMessage");
        if (timerIntervalId){
            clearInterval(timerIntervalId);
            timerIntervalId = null;
        }
        if (countDownDiv)
            countDownDiv.innerHTML = "Waiting for players";
    }
    finalistPlayers[position] = player;

    for (let i = 0; i < 4; i++){
        const playerDiv = document.getElementById(`tournament-player-container-${i}`);
        if (!playerDiv)
            return;
        const finalistPostion = Math.floor(i / 2);
        if (finalistPlayers[finalistPostion]){
            if (finalistPlayers[finalistPostion] != initialPlayers[i] && finalistPlayers[finalistPostion] != " "){
                playerDiv.classList.add('tc-tournament-defeat');
                playerDiv.style.color = "var(--charcoal) !important";
            }
        }
    }

    for (let i = 0; i < 3; i++){
        const playerDiv = document.getElementById(`tournament-player-container-${i + 4}`);
        if (!playerDiv)
            return;
        playerDiv.innerHTML = finalistPlayers[i];
        if (winner != " " && winner != player){
            playerDiv.classList.add('tc-tournament-defeat');
            playerDiv.style.color = "var(--charcoal) !important";
        }
    }
    if (winner != " " && winner != undefined)
        displayWinner();
}

function displayWinner(){
    const winnerDiv = document.getElementById("tournament-player-container-6");
    if (!winnerDiv)
        return;
    winnerDiv.classList.add("tc-tournament-winner-filled");
    if (timerIntervalId){
        clearInterval(timerIntervalId);
        timerIntervalId = null;
    }
    const messageDiv = document.getElementById("tournamentMessage");
    if (!messageDiv)
        return;
    messageDiv.innerHTML = "YOU WON!";
}

function drawLines(){
    const svg = document.querySelector('.tc-tournament-lines');
    if (!svg){
        window.removeEventListener('resize', drawLines);
        return;
    }
    svg.innerHTML = '';
    const positions = [];
    const containerIds = [
        'tournament-player-container-0',
        'tournament-player-container-1',
        'tournament-player-container-2',
        'tournament-player-container-3',
        'tournament-player-container-4',
        'tournament-player-container-5',
        'tournament-player-container-6'
      ];
      const linesToDraw = [
        [0, 4], [1, 4],
        [2, 5], [3, 5],
        [4, 6], [5, 6]
      ];

    containerIds.forEach(id => {
        const participant = document.getElementById(id);
        if (participant) {
            const rect = participant.getBoundingClientRect();
            const position = {
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            };
            positions.push(position);
        }
    })

    const strokeWidth = 8;
    linesToDraw.forEach((pair) => {
        const [startIdx, endIdx] = pair;
        if (positions[startIdx] && positions[endIdx]) {
            const lineH = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            const lineV = document.createElementNS('http://www.w3.org/2000/svg', 'line');

            lineH.setAttribute('x1', positions[startIdx].x);
            lineH.setAttribute('y1', positions[startIdx].y);
            lineH.setAttribute('x2', positions[endIdx].x + strokeWidth / 2);
            lineH.setAttribute('y2', positions[startIdx].y);

            lineV.setAttribute('x1', positions[endIdx].x);
            lineV.setAttribute('y1', positions[startIdx].y);
            lineV.setAttribute('x2', positions[endIdx].x);
            lineV.setAttribute('y2', positions[endIdx].y);

            lineH.setAttribute('stroke', 'white');
            lineH.setAttribute('stroke-width', strokeWidth);
            lineV.setAttribute('stroke', 'white');
            lineV.setAttribute('stroke-width', strokeWidth);
            svg.appendChild(lineV);
            svg.appendChild(lineH);
        }
    });
    svg.innerHTML += ' ';
}

let timeLeft;
let timerIntervalId;
export function startBracketsCountdown(){
    timeLeft = 11;
    if (timerIntervalId){
        clearInterval(timerIntervalId);
    }
    timerIntervalId = setInterval(bracketsTimer, 1000);
    bracketsTimer();
}

function bracketsTimer(){
    timeLeft--;
    const countDownDiv = document.getElementById("tournamentMessage");
    if (!countDownDiv)
        return;
    if (timeLeft <= -1){
        clearInterval(timerIntervalId);
        timerIntervalId = null;
        return;
    }
    countDownDiv.innerHTML = "Starting in: " + timeLeft;
}