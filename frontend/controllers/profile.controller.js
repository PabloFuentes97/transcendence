import Menu from './menu.controller.js'

export default async() => {
	
	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	content.innerHTML = "";

	const div = document.createElement("div");
	div.classList.add("d-flex", "h-100");

	const response = await fetch('../html/profile.html');
	if (!response.ok)
		throw "Profile response !ok";
	div.innerHTML = await response.text();

	content.appendChild(await div);
};