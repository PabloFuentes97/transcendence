
export function setPlayerNames(leftPlayerName, rightPlayerName){

    const rightPlayerNameId = document.getElementById("right-player");
    const leftPlayerNameId = document.getElementById("left-player");

    rightPlayerNameId.innerHTML = rightPlayerName;
    leftPlayerNameId.innerHTML = leftPlayerName;
}

export function setScores(leftScore, rightScore){
    const leftScoreElement = document.getElementById("left-score");
    const rightScoreElement = document.getElementById("right-score");

    leftScoreElement.innerHTML = leftScore;
    rightScoreElement.innerHTML = rightScore;
}