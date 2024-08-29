import { startAnimation } from "../game/game.js";
import Menu from './menu.controller.js'
import { stopBackgroundAnimation } from '../js/background.js'

export default async() => {

	var content = document.querySelector("#app");
	if (!content)
	{
		await Menu();
		content = document.querySelector("#app");
	}
	content.innerHTML = "";

	const response = await fetch('../html/tetris.html');
	if (!response.ok)
		throw "Tetris response !ok";

	content.innerHTML = await response.text();
	stopBackgroundAnimation();
	startAnimation();
};
