import { closeGameSocket, leaveGame } from "./gameSocket.js";
import { closeLoginSocket } from "./login.js";
import { leaveQueue } from "./playModeManager.js";


export default () =>{
    localStorage.removeItem('jwtToken');
    closeGameSocket();
    closeLoginSocket();
}