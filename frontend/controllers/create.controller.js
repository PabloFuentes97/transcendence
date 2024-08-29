import { sendCreateUserRequest } from "../js/createAccount.js"

export default async() => {
    const content = document.getElementById("master");
	if (!content)
		throw "No element master";
    content.innerHTML = "";

    const div = document.createElement("div");
    //let logged = true; 

    const response = await fetch('../html/loginBox.html');
    if (!response.ok)
        throw "Response login !ok";

    div.innerHTML = await response.text();

	let loginResponse = await fetch('../html/createAccount.html');
	if (!loginResponse.ok)
		throw "Login response !ok";

	var app = div.querySelector("#loginbox");
	if (!app)
		throw("Loginbox app error");

	app.innerHTML = await loginResponse.text();
    
    content.appendChild(div);

	const button = document.getElementById("createAccountButton");
	button.addEventListener('click', handleInput);
	document.addEventListener('keypress', handleInput);
}

async function handleInput(event){
    if (!window.location.href.endsWith("#login")){
        document.removeEventListener('keypress', handleLoginInput);        
        return;
    }
    if (event.key === 'Enter' || event.type === "click"){
        if ((await sendCreateUserRequest()))
            document.removeEventListener('keypress', handleInput);
    }
}

export function removeCreateAccountListener(){
	document.removeEventListener('keypress', handleInput);
}