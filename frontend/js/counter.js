var minutesLabel;
var secondsLabel;
var mMIntervalId;
var totalSeconds;

var gameTimer;
var gameGoldenGraffiti;

/* MATCH MAKING TIMER */

export function startMMTimer(){
    totalSeconds = 0;
    minutesLabel = document.getElementById("match-making-minutes");
    secondsLabel = document.getElementById("match-making-seconds");

    mMIntervalId = setInterval(setMMTime, 1000);
    setMMTime();
}

export function stopMMTimer(){
    if (mMIntervalId != null){
        clearInterval(mMIntervalId);
        mMIntervalId = null;
    }
}

function setMMTime()
{

    minutesLabel = document.getElementById("match-making-minutes");
    secondsLabel = document.getElementById("match-making-seconds");

    if (!minutesLabel || !secondsLabel){
        clearInterval(mMIntervalId);
        mMIntervalId = null;
        return;
    }

    ++totalSeconds;
    secondsLabel.innerHTML = pad(totalSeconds%60);
    minutesLabel.innerHTML = pad(parseInt(totalSeconds/60));
}

function pad(val)
{
    var valString = val + "";
    if(valString.length < 2)
    {
        return "0" + valString;
    }
    else
    {
        return valString;
    }
}

/* GAME TIMER */

export function setGameTime(totalSecondsLeft)
{
    totalSecondsLeft = Math.floor(totalSecondsLeft);
    gameTimer = document.getElementById("game-timer");
    if (!gameTimer){
        return;
    }

    if (totalSecondsLeft == 10)
    {
        gameTimer.classList.remove("tc-game-time-black-border")
        gameTimer.classList.add("tc-game-time-red-border")
    }
    if (totalSecondsLeft == -1)
    {
        gameGoldenGraffiti = document.getElementById("golden-graffiti");
        gameGoldenGraffiti.classList.add("tc-game-golden-graffiti")
        gameGoldenGraffiti.classList.remove("tc-invisible-text")
        totalSecondsLeft = 0;
    }
    
    gameTimer.innerHTML = totalSecondsLeft;
}