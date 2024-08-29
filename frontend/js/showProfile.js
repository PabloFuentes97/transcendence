import hideProfile from "./hideProfile.js"
import getUserInfoFromAlias from "./apisCallers/userInfo/getUserInfoFromAlias.js"
import { cacheBypass } from "./settings.js";

let eloChartDiv;
let statsDiv;
export default async(alias) => {
    let profileCanvasDiv = document.getElementById("profileCanvas");

    const userInfo = await getUserInfoFromAlias(alias);

    const div = await fetch('../html/profile.html');
	if (!div.ok)
		throw "Profile response !ok";

    let history = "";
    let totalMatches = 0;
    let totalWins = 0;
    let winrate = 0;
    let totalElo = 0;
    let historyElo = [0];
    const myCurrentElo = userInfo.elo;

    (await userInfo).matchHistory.forEach(match => {
        let sign = '+';
        if (match.elo_earn < 0)
            sign = '';

        let result = (sign == '+')? "Victory" : "Defeat";
        history = `<tr>
        <td>${result}</td>
        <td>${sign}${match.elo_earn}</td>
        <td>${match.match_type}</td>
        <td>${match.userPoints} - ${match.opponentPoints}</td>
        <td>${match.opponent}</td>
        <td>${match.date}</td>
        </tr>` + history;


        totalMatches++;
        historyElo.push(match.elo_earn);
        totalElo += match.elo_earn;
        if (result == "Victory")
                totalWins++;
    })
    winrate = Math.floor(totalWins / totalMatches * 100);

    let divText = await div.text();
    divText = divText.replace('${ranking}', userInfo.ranking);
    divText = divText.replace('${userName}', userInfo.alias);
    divText = divText.replace('${imageUrl}', userInfo.photo_profile);
    divText = divText.replace('${elo}', userInfo.elo);
    divText = divText.replace('${tournamentWins}', userInfo.cups);
    divText = divText.replace('${totalMatches}', totalMatches);
    divText = divText.replace('${wins}', totalWins);
    divText = divText.replace('${winrate}', winrate);
    divText = divText.replace('${history}', history);


    profileCanvasDiv.innerHTML = divText;

    const hideProfileButton = document.getElementById("hideProfile");
    hideProfileButton.addEventListener('click', hideProfile);





    let startingElo = myCurrentElo - totalElo;
    let labels = []
    historyElo.forEach((elo, index) => {
        if (index == 0)
            historyElo[index] += startingElo;
        else
            historyElo[index] += historyElo[index - 1];
        labels.push(index + 1);
    });

    eloChartDiv = document.getElementById('profileEloChart');
    statsDiv = document.getElementById("profileStats");
    resizeChart();
    eloChartDiv.setAttribute('width', eloChartDiv.offsetWidth);
    eloChartDiv.setAttribute('height', eloChartDiv.offsetHeight);
    let ctx = eloChartDiv.getContext('2d');
    let config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'ELO History',
                data: historyElo,
                fill: false,
                borderColor: 'rgb(255, 255, 255)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: false,
                    ticks: {
                        color: 'white' // Change x-axis labels color to white
                    },
                    grid: {
                        color: '#555555' // Change x-axis grid lines to grey
                    }
                },
                y: {
                    beginAtZero: false,
                    ticks: {
                        color: 'white' // Change x-axis labels color to white
                    },
                    grid: {
                        color: '#555555' // Change x-axis grid lines to grey
                    }
                }
            }
        }
    }

    let eloChart = new Chart(ctx, config);

    window.addEventListener('resize', resizeChart);

    document.addEventListener('click', detectClickOutsideCard);
}

function resizeChart(){
    eloChartDiv = document.getElementById('profileEloChart');
    if (!eloChartDiv ||eloChartDiv == undefined){
        window.removeEventListener('resize', resizeChart);
        return;
    }
    eloChartDiv.parentNode.style.height = statsDiv.offsetHeight + "px";
}


function detectClickOutsideCard(event){
    
    const cardDiv = document.getElementById("profileCard");
    if (cardDiv == null){
        document.removeEventListener('click', detectClickOutsideCard);
        return;
    }
    
    if (!cardDiv.contains(event.target)){
        hideProfile();
        document.removeEventListener('click', detectClickOutsideCard);
    }
}
