import showProfile from "../js/showProfile.js"
import logOut from "../js/logOut.js"
import getMyUserInfo from "../js/apisCallers/userInfo/getMyUserInfo.js";

export default async() => {
	
	var content = document.getElementById("master");
    content.innerHTML = "";

    let menu = document.createElement("div");
    menu.classList.add("row");
    menu.classList.add("g-0");

    let menuResponse = await fetch('../html/mainMenu.html');
    if (!menuResponse.ok)
        throw "Menu response !ok";
    menu.innerHTML = await menuResponse.text();
    
    content.appendChild(await menu);

    const profilePicture = document.getElementById("menu-profilePicture");
    profilePicture.addEventListener('click', showSelfProfile);

    const logOutElement = document.getElementById("logOutButton");
    logOutElement.addEventListener('click', logOut);

    const info = await getMyUserInfo();
    if (info != null)
	    profilePicture.style.backgroundImage = "url(" + await info.photo_profile + ")";
};

async function showSelfProfile(alias){
    
    const userInfo = await getMyUserInfo();
    showProfile(userInfo.alias);
}