import { connectLoginSocket } from "./login.js";

export function sendLoginIntraRequest() {

    const URL = `https://${window.location.host}/auth_service/start_auth_intra/`;
    const width = 600;
    const height = 700;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    const oauthWindow = window.open(URL, 'oauthWindow', `width=${width},height=${height},top=${top},left=${left}`);
    
    if (oauthWindow) {
        const checkPopupClosed = setInterval(() => {
            if (oauthWindow.closed) {
                const jwtToken = localStorage.getItem('jwtToken');
                if (jwtToken) {
                    window.localStorage.setItem('jwtToken', jwtToken);
                    window.location.href = '#home';
                    connectLoginSocket();
                    clearInterval(checkPopupClosed);
                }
            }
        }, 2000);
    
        setTimeout(() => {
            clearInterval(checkPopupClosed);
            if (!oauthWindow.closed) {
                oauthWindow.close();
            }
        }, 120000);
    } 
}
