let loginSocket;

export function connectLoginSocket() {
    loginSocket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/login/?token='
            + localStorage.getItem('jwtToken')
    );

    loginSocket.onclose = function(e) {
        console.error('game socket closed unexpectedly');
    };
}

export function closeLoginSocket(){
    loginSocket.onclose = function () {};
    loginSocket.close();
    loginSocket = null;
}

export async function sendLoginRequest() {
    const usernameDiv = document.getElementById('username');
    if (!usernameDiv)
        return;
    const username = usernameDiv.value;
    const passwordDiv = document.getElementById('password');
    if (!passwordDiv)
        return;
    const password = passwordDiv.value;
    const otp = document.getElementById('otp') ? document.getElementById('otp').value : null;

    const requestData = { username, password };
    if (otp) requestData.otp = otp;

    const response = await fetch('/auth_service/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    });
    if (!response.ok){
        const errorData = await response.json();
        const failDiv = document.getElementById('failInfo');
        if (failDiv)
            failDiv.innerHTML = errorData.error;
        return;
    }
    
    const data = await response.json();

    if (data.requires2FA) {
        document.getElementById('failInfo').textContent = ""
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('otp-form').style.display = 'block';
    } else {
        localStorage.setItem('jwtToken', (await data).token);
        window.location.href = '#home';
        connectLoginSocket();
    }
    return true;
}

function handle2FAInput(event){

}
