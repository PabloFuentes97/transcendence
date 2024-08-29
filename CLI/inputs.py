import asyncio
from pynput import keyboard
import time
import json

player1_input = None
player2_input = None
esc = False

def set_offline_keys():

    global player1_input, player2_input
    player1_input = None
    player2_input = None
    def on_press(key):
        global player1_input, player2_input

        if (hasattr(key, "char") and key.char == 'w'):
            player1_input = "UP"
        elif (hasattr(key, "char") and key.char == 's'):
            player1_input = "DOWN"
        if key == keyboard.Key.up:
            player2_input = "UP"
        elif key == keyboard.Key.down:
            player2_input = "DOWN"
        else:
            pass

    def on_release(key):
        global player1_input, player2_input
        
        if hasattr(key, "char") and key.char == 'w' and player1_input == "UP":
            player1_input = None
        elif hasattr(key, "char") and key.char == 's' and player1_input== "DOWN":
            player1_input = None
        if key == keyboard.Key.up and player2_input == "UP":
            player2_input = None
        elif key == keyboard.Key.down and player2_input == "DOWN":
            player2_input = None
        else:
            pass
    
    keyboard.Listener(on_press=on_press, on_release=on_release).start()

def set_online_keys():
    global player1_input
    player1_input = None
    def on_press(key):
        global player1_input

        if key == keyboard.Key.up:
            player1_input = "UP"
        elif key == keyboard.Key.down:
            player1_input = "DOWN"

    def on_release(key):
        global player1_input
        if key == keyboard.Key.up and player1_input == "UP":
            player1_input = None
        elif key == keyboard.Key.down and player1_input == "DOWN":
            player1_input = None
    
    keyboard.Listener(on_press=on_press, on_release=on_release).start()
    
TIME_FRAME = 16

async def offline_inputs(ws):
    global player1_input, player2_input
    set_offline_keys()
    curr_time = time.time() * 1000
    start_time = curr_time

    while True:
        curr_time = time.time() * 1000
        if curr_time >= start_time + TIME_FRAME:

            if player1_input or player2_input:
                send_dict = {
                    "type": "update_input",
                    "mode": "offline"
                }
                if player1_input:
                    send_dict["0"] = player1_input
                if player2_input:
                    send_dict["1"] = player2_input
                await ws.send(json.dumps(send_dict))
            
            start_time = curr_time
        await asyncio.sleep(0.01)
    
async def online_inputs(ws):
    global player1_input
    set_online_keys()
    curr_time = time.time() * 1000
    start_time = curr_time

    while True:
        curr_time = time.time() * 1000
        if curr_time >= start_time + TIME_FRAME:

            if player1_input:
                send_dict = {
                    "type": "update_input",
                    "mode": "online",
                    "key": player1_input
                }
                await ws.send(json.dumps(send_dict))

            start_time = curr_time
        await asyncio.sleep(0.01)