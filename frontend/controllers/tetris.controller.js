import { startAnimation } from "../game/game.js";
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

	const response = await fetch('../html/tetris.html');
	if (!response.ok)
		throw "Tetris response !ok";
	div.innerHTML = await response.text();

	content.appendChild(await div);
	startAnimation();
	div.addEventListener('unload', hello);
};