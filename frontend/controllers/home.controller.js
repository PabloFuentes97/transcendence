import Menu from './menu.controller.js'

export default async() => {
	
	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	let response = await fetch(`../html/home.html`);
	if (!response.ok)
		throw "Home response !ok";

	content.innerHTML = await response.text();

};