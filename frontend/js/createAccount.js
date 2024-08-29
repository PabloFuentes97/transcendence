import { connectLoginSocket } from "./login.js";

export async function sendCreateUserRequest() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const passwordRep = document.getElementById('passwordRepeat').value;
    const failInfo = document.getElementById('failInfoRegister');
    failInfo.value = '';
    
    if (password !== passwordRep) {
        failInfo.textContent = 'Passwords do not match.';
        return;
    }
    
    if (password.length > 80) {
        failInfo.textContent = 'Password must be 80 characters or less.';
        return;
    }

    try {
        const response = await fetch('/auth_service/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username, password: password })
        });

        if (!response.ok){
            const errorData = await response.json();
            throw new Error(errorData.error);
        }
        const data = await response.json();
        localStorage.setItem('jwtToken', data.token);
        window.location.href = '#home';
        connectLoginSocket();
        return true;
    } catch (error){
        failInfo.textContent = error.message;
        return false;
    }
}

