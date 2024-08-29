import { sendLoginRequest } from "../js/login.js";
import { sendCreateUserRequest } from "../js/createAccount.js";
import { sendLoginIntraRequest } from "../js/loginIntra.js";
import { removeCreateAccountListener } from "./create.controller.js";

export default async () => {
    const content = document.getElementById("master");
    if (!content) throw "No element master";
    content.innerHTML = "";

    const div = document.createElement("div");

    const response = await fetch('../html/loginBox.html');
    if (!response.ok) throw "Response login !ok";

    div.innerHTML = await response.text();
    content.appendChild(div);

    await loadLoginBox();
};

async function loadLoginBox() {
    let response = await fetch('../html/login.html');
    if (!response.ok) throw "Login response !ok";

    var app = document.querySelector("#loginbox");
    if (!app) throw "Loginbox app error";

    app.innerHTML = await response.text();

    document.addEventListener('keypress', handleLoginInput);
    
    const logInButton = document.getElementById("logInButton");
    logInButton.addEventListener('click', handleLoginInput);

    const loginWithIntraButton = document.getElementById("loginWithIntra");
    loginWithIntraButton.addEventListener('click', sendLoginIntraRequest);
    

    const verifyOptButton = document.getElementById("verifyOtpButton");
    verifyOptButton.addEventListener('click', handleLoginInput);

    const registerElememnt = document.getElementById("registration");
    registerElememnt.addEventListener('click', loadCreateAccountBox);

    removeCreateAccountListener();
}

async function handleLoginInput(event){
    if (!window.location.href.endsWith("#login")){
        document.removeEventListener('keypress', handleLoginInput);        
        return;
    }
    if (event.key === 'Enter' || event.type === "click"){
        if ((await sendLoginRequest())){
            document.removeEventListener('keypress', handleLoginInput);
        }
    }
}

async function loadCreateAccountBox (){

    document.removeEventListener('keypress', handleLoginInput);
    const response = await fetch('../html/createAccount.html');
    if (!response.ok) throw "Response login !ok";

    var app = document.querySelector("#loginbox");
    if (!app) throw "Loginbox app error";

    app.innerHTML = await response.text();

	const button = document.getElementById("createAccountButton");

	button.addEventListener('click', handleCreateInput);
	document.addEventListener('keypress', handleCreateInput);

    const goBackElement = document.getElementById("backToLogin");
    goBackElement.addEventListener('click', loadLoginBox);
}

async function handleCreateInput(event){
    if (!window.location.href.endsWith("#login")){
        document.removeEventListener('keypress', handleLoginInput);        
        return;
    }
    if (event.key === 'Enter' || event.type === "click"){
        if ((await sendCreateUserRequest()))
            document.removeEventListener('keypress', handleCreateInput);
    }
}