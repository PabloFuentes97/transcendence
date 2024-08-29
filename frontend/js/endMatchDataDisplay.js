import { pages } from "../controllers/index.js";
import { stopAnimation } from "../game/game.js";
import { elo } from "./apisCallers/userInfo/myProfileGetters.js";
import { startBackgroundAnimation } from "./background.js";
import { loadTournamentBrackets } from "./tournamentManager.js";
import * as gameSocket from "./gameSocket.js"

let mode;
let timerDiv;
let timeLeft;
let timerIntervalId;
let result;

let eloObtainedDiv;
let eloObtainedCurrVal;
let eloObtainedMax;
let eloObtainedSign;
let eloObtainedIntervalId;
const eloObtainedAnimationTime = 3000;
let eloObtainedAnimationStartTime;

let eloFinalDiv;
let eloFinalCurrVal;
let eloFinalMax;
let eloFinalIntervalId;
const eloFinalAnimationTime = 3000;
let eloFinalAnimationStartTime;
const eloFinalAnimationDelay = 500;

export async function loadEndMatchData (data) {

    const response = await fetch('../html/endMatchScreen.html');
	if (!response.ok)
		throw response.statusText;

    const div = document.getElementById("app");
    if (!div)
        return;

    let popUpBox = await response.text();
    let myCurrentElo;
    
    if (data["mode"] == 'local'){
        popUpBox = popUpBox.replace('${display-result}', 'local')
        popUpBox = popUpBox.replace('${Result}', "Results");
        popUpBox = popUpBox.replace('${Player1}', "Player1");
        popUpBox = popUpBox.replace('${Player2}', "Player2");
        popUpBox = popUpBox.replace('${Elo}', '');
    }
    else{
        myCurrentElo = await elo();
        (await myCurrentElo);
        result = (data.result.toLowerCase() == "defeat")? "defeat" : "victory";
        popUpBox = popUpBox.replace('${display-result}', result)
        popUpBox = popUpBox.replace('${Result}', result);
        popUpBox = popUpBox.replace('${Player1}', data.players[0]);
        popUpBox = popUpBox.replace('${Player2}', data.players[1]);
        popUpBox = popUpBox.replace('${Elo}', myCurrentElo - data.elo_earned);
    }

    popUpBox = popUpBox.replace('${Final Score}', data.score[0] + ' - ' + data.score[1]);

    mode = data.mode;

    div.innerHTML += popUpBox;
    
    const returnButton = document.getElementById("end-return");
    if (returnButton)
        returnButton.addEventListener('click', returnBack);

    timerDiv = document.getElementById("matchEnd-Timer");
    timeLeft = 10;
    if (data["mode"] == 'local')
        timeLeft = 20;
    returnTimer();
    timerIntervalId = setInterval(returnTimer, 1000);
    
    //Cosas del elo

    eloObtainedDiv = document.getElementById("elo-obtained");
    eloFinalDiv = document.getElementById("elo-result");

    if (data["mode"] == 'local'){
        eloObtainedDiv.innerHTML = '';
        eloFinalDiv.innerHTML = '';
    }
    else{
        eloObtainedCurrVal = 0;
        eloObtainedSign = Math.sign(data.elo_earned);
        eloObtainedMax = Math.abs(data.elo_earned);
        eloObtainedAnimationStartTime = Date.now();

        eloFinalMax = myCurrentElo;
        eloFinalCurrVal = myCurrentElo - data.elo_earned;
        eloObtainedIntervalId = setInterval(eloObtainedAnim, 100);
        eloObtainedAnim();
    }

}

function returnTimer(){
    timerDiv = document.getElementById("matchEnd-Timer");
    if (!timerDiv){
        timerDiv = undefined;
        if (timerIntervalId != undefined){
            clearInterval(timerIntervalId);
            timerIntervalId = undefined;
        }
        return;
    }
    if (timeLeft <= 0){
        clearInterval(timerIntervalId);
        timerIntervalId = undefined;
		returnBack();
    }
    timerDiv.innerHTML = `Leaving in ${timeLeft}`;
    
    timeLeft--;
}

function returnBack(){
    if (timerIntervalId != undefined){
        clearInterval(timerIntervalId);
        timerIntervalId = undefined;
    }
    startBackgroundAnimation();
    if (mode == 'tournament' && result == 'victory'){
        startBackgroundAnimation();
        loadTournamentBrackets();
        gameSocket.send(JSON.stringify({
            "type": "tournament_user_ready"}));
    }
    else{
        gameSocket.idle();
        pages.play();
    }
}

function eloObtainedAnim(){

    if (!timerDiv){
        if (eloObtainedIntervalId != undefined){
            clearInterval(eloObtainedIntervalId);
            eloObtainedIntervalId = undefined;
        }
        return;
    }

    let animationCurrentTime = Date.now() - eloObtainedAnimationStartTime;
    let animationPercentaje = animationCurrentTime / eloObtainedAnimationTime;

    if (animationPercentaje >= 1)
        animationPercentaje = 1;
    eloObtainedCurrVal = Math.floor(easeOutCubic(animationPercentaje) * eloObtainedMax);

    if (eloObtainedSign == 1)
        eloObtainedDiv.innerHTML = "+" + eloObtainedCurrVal;
    else
        eloObtainedDiv.innerHTML = "-" + eloObtainedCurrVal;
    
    if (animationPercentaje == 1)
    {
        eloFinalAnimationStartTime = Date.now() + eloFinalAnimationDelay;
        eloFinalIntervalId = setInterval(eloFinalAnim, 100);
        clearInterval(eloObtainedIntervalId);
    }
}

function eloFinalAnim(){

    if (!timerDiv){
        if (eloFinalIntervalId != undefined){
            clearInterval(eloFinalIntervalId);
            eloFinalIntervalId = undefined;
        }
        return;
    }

    let animationCurrentTime = Date.now() - eloFinalAnimationStartTime;
    let animationPercentaje = animationCurrentTime / eloFinalAnimationTime;

    if (animationPercentaje >= 1)
        animationPercentaje = 1;
    else if (animationPercentaje < 0)
        return;
    let eloObtainedAnimatedValue = Math.floor(easeOutCubic(animationPercentaje) * eloObtainedMax * eloObtainedSign);
    let val = eloFinalCurrVal + eloObtainedAnimatedValue;
    eloFinalDiv.innerHTML = val + " pps";

    if(animationPercentaje == 1){
        clearInterval(eloFinalIntervalId);
        eloFinalIntervalId = undefined;
    }
}

function easeOutCubic(time){
    return 1 - Math.pow(1 - time, 3);
}

