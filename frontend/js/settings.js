import { userInfo } from './apisCallers/userInfo/userInfo.index.js';
import * as profileGetters from './apisCallers/userInfo/myProfileGetters.js';
import showNotification from '../js/showNotification.js'
import { createFlashbang } from './flashbang.js';
import changePassword from './apisCallers/auth/changePassword.js';
import * as gameSocket from './gameSocket.js';

let settingsAliasInput;
let settingsImageInput;
let settingsSaveButton;
let settingsOldPassInput;
let settingsNewPassInput;
let settingsNewPassRepeatInput;
let flashbangButton;
let isAliasFree = false;
let aliasFreeMessage = "";
let firstLoad = true;

export function setSettingsListeners(){

    updateElements();
    updateAliasPlaceholder();

	settingsAliasInput.addEventListener('blur', () => { checkAlias(); });
	settingsSaveButton.addEventListener('click', () =>{ saveSettings(); });
	settingsNewPassRepeatInput.addEventListener('blur', () => { checkRepeatedPassword(); });
	settingsNewPassInput.addEventListener('blur', () => { checkRepeatedPassword(); });
	flashbangButton.addEventListener('click', createFlashbang);
}

function updateElements(){
    settingsAliasInput = document.getElementById("settings-alias");
    settingsImageInput = document.getElementById("settings-imageInput");
    settingsSaveButton = document.getElementById("settings-saveSettingsButton");
    settingsOldPassInput = document.getElementById("settings-oldPassword");
    settingsNewPassInput = document.getElementById("settings-newPassword");
    settingsNewPassRepeatInput = document.getElementById("settings-newPasswordRepeated");
	flashbangButton = document.getElementById("settings-changeTheme");
}

async function updateAliasPlaceholder(){
	if (!settingsAliasInput)
		return;

    settingsAliasInput.value = "";
    const alias = await userInfo.myProfile.getMyAlias();
	settingsAliasInput.placeholder = alias;

	if (firstLoad){
		firstLoad = false;
		return;
	}
	gameSocket.updateAlias(alias);
}

async function checkAlias(){
	const checkDiv = document.getElementById("settings-aliasCheck");

	if (settingsAliasInput.value != ""){
		const currentAlias = await userInfo.myProfile.getMyAlias();
		if (currentAlias != null){
			if (settingsAliasInput.value == currentAlias){
				isAliasFree = false;
				aliasFreeMessage = "this is your current alias"
			}
			else{
				aliasFreeMessage = await userInfo.aliasAvailable(settingsAliasInput.value);
				if (aliasFreeMessage == "ok")
					isAliasFree = true;
				else{
					isAliasFree = false;
					aliasFreeMessage = aliasFreeMessage.toLocaleLowerCase().replace('username', 'alias');
				}
			}
		}
		
		if (isAliasFree){
			checkDiv.innerHTML = '<i class="bi bi-check-lg" style="color: var(--correct)">alias is available</i>';
		}else{
			checkDiv.innerHTML = `<i class="bi bi-x-lg" style="color: var(--wrong);"> ${aliasFreeMessage}</i>`;
		}
	}
	else{
		isAliasFree = false;
		checkDiv.innerHTML = "";
	}
	return isAliasFree;
}


function checkRepeatedPassword(){
	const passCheckIcon = document.getElementById("settings-passwordCheckIcon");

	passCheckIcon.innerHTML = "";

	if (settingsNewPassInput.value != settingsNewPassRepeatInput.value && settingsNewPassRepeatInput.value != ""){
		passCheckIcon.innerHTML = '<i class="bi bi-x-lg" style="color: var(--wrong)">passwords do not match</i>';
		return false;
	}
	else if (settingsNewPassInput.value == "" && settingsNewPassRepeatInput.value == "")
		return false;
	return true;
}


async function saveSettings(){
	const errorDiv = document.getElementById("settings-saveSettingsProblem");
	let somethingChanged = false;

	errorDiv.innerHTML = "";

	if (isAliasFree && settingsAliasInput.value){
		somethingChanged = true;
		await userInfo.changeAlias(settingsAliasInput.value);
		updateAliasPlaceholder();
		const checkDiv = document.getElementById("settings-aliasCheck");
		if (checkDiv)
			checkDiv.innerHTML = "alias has been updated";
	}


	const file = settingsImageInput.files[0];

	if (file){
		if (file.size / 1024 / 1024 > 42){
			errorDiv.innerHTML = "Error: Image is too large";
			return;
		}
        const data = userInfo.uploadProfilePhoto(file);
		if (await data == 413){
			errorDiv.innerHTML = "Error: Image is too large";
			return;
		}
		else if (await data == 200){
        	reloadMenuProfilePicture();
			somethingChanged = true;
		}
		else{
			showNotification("Error saving the new profile picture, try again later");
		}
    }

	const passCheckIcon = document.getElementById("settings-oldPasswordCheckIcon");
	passCheckIcon.innerHTML = ''

	if (settingsOldPassInput.value || settingsNewPassInput.value || settingsNewPassRepeatInput.value){
		if (checkRepeatedPassword()){
			const oldPassword = settingsOldPassInput.value;
			const newPassword = settingsNewPassInput.value;
			let changePasswordStatus = await changePassword(newPassword, oldPassword);
			if (changePasswordStatus == 200){
				somethingChanged = true;
				settingsOldPassInput.value = '';
				settingsNewPassInput.value = '';
				settingsNewPassRepeatInput.value = '';
				passCheckIcon.innerHTML = '<i class="bi bi-check-lg" style="color: var(--correct)"> password changed</i>'
			}
			else{
				passCheckIcon.innerHTML = '<i class="bi bi-x-lg" style="color: var(--wrong)"> wrong password</i>'
			}
		}
	}

	if (somethingChanged)
		showNotification("New settings saved");
	else
		showNotification("Nothing changed");
}

export let cacheBypass = 0;
async function reloadMenuProfilePicture(){
	const menuProfilePicture = document.getElementById("menu-profilePicture");

	const imageUrl = await profileGetters.getMyProfilePicture();
	if (await imageUrl){
		cacheBypass = (cacheBypass + 1) % 2;
		menuProfilePicture.style.backgroundImage = "url(" + (await imageUrl) + `?t=${cacheBypass}` + ")"
	}
} //HAY QUE CAMBIAR ESTO A BACKGROUND