import Menu from './menu.controller.js'
import { setSettingsListeners } from '../js/settings.js';
import { checkTwoFactorAuthStatus } from '../js/apisCallers/auth/twoFactorAuth.js';

export default async function()  {
    var content = document.querySelector("#app");
    if (!content)
    {
        await Menu();
        content = document.querySelector("#app");
    }
    content.innerHTML = "";


    const response = await fetch('../html/settings.html');
    if (!response.ok)
        throw "Social response !ok";
    content.innerHTML = await response.text();

    setSettingsListeners();
    await checkTwoFactorAuthStatus(); // Check and set two-factor auth status
};
