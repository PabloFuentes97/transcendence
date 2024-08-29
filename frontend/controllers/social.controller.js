import acceptFriendRequest from '../js/apisCallers/userInfo/acceptFriendRequest.js';
import declineFriendRequest from '../js/apisCallers/userInfo/declineFriendRequest.js';
import removeFriendWithAlias from '../js/apisCallers/userInfo/removeFriend.js';
import getFriendRequests from '../js/apisCallers/userInfo/getFriendRequests.js';
import getFriends from '../js/apisCallers/userInfo/getFriends.js';
import getAllUsers from '../js/apisCallers/userInfo/getAllUsersInfo.js'
import getUserInfo from '../js/apisCallers/userInfo/getUserInfo.js';
import getUserInfoFromAlias from '../js/apisCallers/userInfo/getUserInfoFromAlias.js'
import * as profileGetters from '../js/apisCallers/userInfo/myProfileGetters.js';
import sendFriendRequest from "../js/apisCallers/userInfo/sendFriendRequest.js";
import Menu from './menu.controller.js'
import showNotification from '../js/showNotification.js'

export default async() => {
	
	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	content.innerHTML = "";

	const response = await fetch('../html/social.html');
	if (!response.ok)
		throw "Social response !ok";

	content.innerHTML = await response.text();
	setListeners();
	displayComunity();
};

function setListeners(){
	const socialViewDiv = document.getElementById("socialView");
	socialViewDiv.addEventListener("click", e => {
		if (e.target.id == "friendsButton")
			displayFriends();
		else if (e.target.id == "comunityButton")
			displayComunity();
		else if (e.target.id == "friendRequestButton")
			displayFriendRequests();
		else if (e.target.id == "acceptFriendRequestButton" || e.target.closest.id == "acceptFriendRequestButton")
			acceptFriend(e.target);
		else if (e.target.id == "declineFriendRequestButton" || e.target.closest.id == "declineFriendRequestButton")
			declineFriend(e.target);
		else if (e.target.id == "social-removeFriend" || e.target.closest.id == "social-removeFriend")
			removeFriend(e.target);
		else if (e.target.id == "social-sendFriendRequest" || e.target.closest.id == "social-sendFriendRequest")
			sendRequest(e.target);
	})
}

async function displayComunity(){
	selectMenuOption("comunity");

	let table = document.getElementById("socialUsersDisplay");
	table.innerHTML = "";

	var userList = getAllUsers();

	if (!userList)
		return;

	userList = (await userList).users;
	const myUserAlias = profileGetters.getMyAlias();

	for (let i = 0; i < userList.length; i++){
		let user = userList[i];
		if (user.alias == (await myUserAlias))
			continue;
		let userLabel = `
		<div class="d-flex tc-user-card tc-border tc-background-hyperdark p-2 justify-content-between">
			<div class="tc-square-image tc-user-card-image" id="profile-image" alias="${user.alias}" style="background-image: url(${user.photo_profile});"></div>
			<div class="d-flex flex-column mx-2 w-100 justify-content-between">
				<div>${user.alias}</div>
				<div class="d-flex">
					<i class="btn bi bi-person-fill-add" id="social-sendFriendRequest" alias="${user.alias}"></i>
				</div>
			</div>
		</div>`
		
		table.innerHTML += userLabel;
	}
}

async function displayFriends(){
	selectMenuOption("friends");

	let table = document.getElementById("socialUsersDisplay");
	table.innerHTML = `
	<div class="w-100 d-flex flex-column">
		<div class="w-100 mb-2 tc-users-state-separator">Online</div>
		<div class="w-100 d-flex flex-wrap mb-4 gap-2" id="onlineUsers"></div>

		<div class="w-100 mb-2 tc-users-state-separator">Offline</div>
		<div class="w-100 d-flex flex-wrap mb-4 gap-2" id="offlineUsers"></div>
	</div>
	`;


	const onlineTalbe = document.getElementById("onlineUsers");
	const offlineTalbe = document.getElementById("offlineUsers");

	var userList = await getFriends();
	
	if ((await userList) == null || userList.friends.length == 0){
		table.innerHTML += "No friends? So sad";
		return;
	}
	userList = userList.friends;
	for (let i = 0; i < userList.length; i++){
		let user = userList[i];

		let userStatusClass = "";
		if (user.status == "Offline")
			userStatusClass = "tc-filter-greyscale";

		let userLabel = `
		<div class="d-flex tc-user-card tc-border tc-background-hyperdark p-2 justify-content-between" id="friendNumber${i}">
			<div class="tc-square-image tc-user-card-image ${userStatusClass}" id="profile-image" alias="${user.alias}" style="background-image: url(${user.photo_profile});"></div>
			<div class="d-flex flex-column mx-2 w-100 justify-content-between">
				<div>${user.alias}</div>
				<div class="d-flex">
					<i class="btn bi bi-x-circle-fill" id="social-removeFriend" alias="${user.alias}" index="${i}"></i>
				</div>
			</div>
		</div>`

		if (user.status == "Online")
			onlineTalbe.innerHTML += userLabel;
		else
			offlineTalbe.innerHTML += userLabel;
	}
}

function sendRequest(target){

	const alias = target.getAttribute("alias");
	if (alias == null)
		return;
	sendFriendRequest(alias);
	showNotification('Friend request sent to ' + alias);
}

async function displayFriendRequests(){
	selectMenuOption("requests");

	let table = document.getElementById("socialUsersDisplay");
	table.innerHTML = "";

	let userList = getFriendRequests();
	if (!(await userList) || (await userList).friend_requests.length == 0)
		return;

	userList = (await userList).friend_requests;
	for (let i = 0; i < userList.length; i++){
		let user = userList[i];

		let userLabel = `
		<div class="d-flex tc-user-card tc-border tc-background-hyperdark p-2 justify-content-between" id="requestNumber${i}">
			<div class="tc-square-image tc-user-card-image" id="profile-image" alias="${user.alias}" style="background-image: url(${user.photo_profile});"></div>
			<div class="d-flex flex-column mx-2 w-100 justify-content-between">
				<div>${user.from_user}</div>
				<div class="d-flex gap-1">
					<i class="btn bi bi-check-circle-fill" alias="${user.from_user}" index="${i}" id="acceptFriendRequestButton"></i>
					<i class="btn bi bi-x-circle-fill" alias="${user.from_user}" index="${i}" id="declineFriendRequestButton"></i>
				</div>
			</div>
		</div>`
		
		table.innerHTML += userLabel;
	}

}

function acceptFriend(target){
	
	const alias = target.getAttribute("alias");
	const index = target.getAttribute("index");

	
	acceptFriendRequest(alias);
	removeFriendRequest(index);
	showNotification("Friend request accepted");
}

function declineFriend(target){
	
	const alias = target.getAttribute("alias");
	const index = target.getAttribute("index");

	declineFriendRequest(alias);
	removeFriendRequest(index);
	showNotification("Friend request rejected");
}

function removeFriendRequest(index){

	const requestDiv = document.getElementById("requestNumber" + index);
	requestDiv.remove();
}

function removeFriend(target){

	const alias = target.getAttribute("alias");
	const index = target.getAttribute("index");

	const friendDiv = document.getElementById("friendNumber" + index);
	friendDiv.remove();

	removeFriendWithAlias(alias);
	showNotification(alias + " is no longer your friend");
}

// Input: string
// Options: "friends", "comunity", "requests"
function selectMenuOption(option){
	const friendsButton = document.getElementById("friendsButton");
	const comunityButton = document.getElementById("comunityButton");
	const friendRequestsButton = document.getElementById("friendRequestButton");

	friendsButton.classList.remove("tc-selected");
	comunityButton.classList.remove("tc-selected");
	friendRequestsButton.classList.remove("tc-selected");

	if (option == "friends")
		friendsButton.classList.add("tc-selected");
	else if (option == "comunity")
		comunityButton.classList.add("tc-selected");
	else if (option == "requests")
		friendRequestsButton.classList.add("tc-selected");
	
}