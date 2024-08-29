import { setGameTime } from './counter.js';

let countdownSecondsLabel;
let cIntervalId;

let startTime;
let currTime;
let fractionOfSecond;
let twoDecimalsStr;
let twoDecimalsNumber;

const countdownSeconds = 3;

export function startCountdown(gameDur){
    
    countdownSecondsLabel = document.getElementById("countdown-text");
    setGameTime(gameDur);

    startTime = Date.now();
    setCTime();
    cIntervalId = setInterval(setCTime, 10);
}

function setCTime()
{
    currTime = countdownSeconds - (Date.now() - startTime) / 1000;
    fractionOfSecond = currTime - Math.floor(currTime);

    twoDecimalsStr = fractionOfSecond.toFixed(2);

    twoDecimalsNumber = parseFloat(twoDecimalsStr);
    
    countdownSecondsLabel.style.scale = fractionOfSecond;

    countdownSecondsLabel.innerHTML = Math.floor(currTime) + 1;

    if (currTime <= 0)
        countdownSecondsLabel.innerHTML = "GO";
    
    if (currTime < -1)
    {
        countdownSecondsLabel.style.scale = "0";
        clearInterval(cIntervalId);
    }
}