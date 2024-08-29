import Menu from './menu.controller.js'
import getPodiumUsers from '../js/apisCallers/userInfo/getPodiumUsers.js'
import getMyUserInfo from '../js/apisCallers/userInfo/getMyUserInfo.js'
import { cacheBypass } from '../js/settings.js';

export default async() => {
	
	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	let response = await fetch('../html/leaderboard.html');
	if (!response.ok)
		throw "Home response !ok";

	let homeText = await response.text();
	homeText = loadLeaderBoard(homeText);
	content.innerHTML = (await homeText);
};

async function loadLeaderBoard(text){

	let topPlayers = await getPodiumUsers();

	const user = await getMyUserInfo();

	topPlayers = topPlayers.users;

	if (user.ranking >= 10)
		topPlayers[9] = user;

	let table = "";
	topPlayers.forEach((player, index) => {
		if (!(player == undefined || player == null)){
			if (index < 3)
				text = addToPodium(player, index + 1, text);
			if (user.ranking > 10 && index == 9)
				table += addToTable(player, user.ranking, user.ranking);
			else
				table += addToTable(player, index + 1, user.ranking);
		}
			
	})
	if (topPlayers.length < 3)
		text = text.replace("{podium3Style}", "display: none !important;");
	else
		text = text.replace("{podium3Style}", "");
		
	if (topPlayers.length < 2)
		text = text.replace("{podium2Style}", "display: none !important;");
	else
		text = text.replace("{podium2Style}", "");

	text = text.replace("${dashboardTable}", table);
	text = text.replace("${podium2}", "");
	text = text.replace("${podium3}", "");
	return text;
}

function addToPodium(player, rank, text){
	let podiumContent = `
	<div type="button" class="h-100 me-3 tc-square-image" style="background-image: url(${player.photo_profile});" id="profile-image" alias="${player.alias}">
	</div>
	<div class="d-flex flex-column align-items-center mx-auto">
		<div>${player.alias}</div>
		<div>${player.elo}</div>
	</div>
	`
	text = text.replace("${podium" + rank + "}", podiumContent);
	return text;
}

function addToTable(player, rank, userRank){
	const wins = (player.wins == undefined)? 0 : player.wins;
	let userClass = "";
	if (userRank == rank)
		userClass = 'class="tc-leaderboard-table-user"'

	let tableRow = `
	<tr ${userClass}>
		<td>${rank}</td>
		<td><div class="p-2" style="height: 8.8vh;"><div type="button" class="tc-square-image" style="background-image: url(${player.photo_profile}); height: 100% !important" id="profile-image" alias="${player.alias}"></div></div></td>
		<td><span class="text-content">${player.alias}</span></td>
		<td>${player.elo}</td>
		<td>${wins}</td>
	</tr>
	`;

	return tableRow;
}