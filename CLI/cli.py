import requests
import asyncio
import time
import json
import websockets
import inputs
from pynput import keyboard
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import ssl
from math import ceil, floor
import atexit
import signal 
import os
import psutil

curses_state = False
stdscr = None

MIN_W = 80
MIN_H = 20
ASPECT_RATIO = 4

def float_to_int(n):
    res = n % 1 * 10
    print(res)
    if res >= 5:
        return ceil(n)
    else:
        return floor(n)

def init_curses():
    global stdscr
    global curses_state
    stdscr = curses.initscr()
    curses.start_color()
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.keypad(1)
    try:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    except Exception as e:
        exit(1)
    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
    curses_state = True

def clean_curses():
    global curses_state
    if curses_state:
        global stdscr
        stdscr.erase()
        #return terminal to normal state
        stdscr.keypad(0)
        curses.echo() ; curses.nocbreak()
        curses.endwin()
        curses_state = False

def handler(signum, frame):
    print("Ctrl-C")
    clean_curses()
    exit(1)

signal.signal(signal.SIGINT, handler)

def point_transform_coordinates(pos, coord_dest, coord_src):

    dw = coord_dest[0] / coord_src[0]
    dh = coord_dest[1] / coord_src[1]

    new_pos = [pos[0] * dw, pos[1] * dh]

    return new_pos


def transform_point(point, origin_coord, playfield_coord, win_coord):
    
    #1) Cambiar origen dentro de sistema de coordenadas local de cada objeto
    point[0] -= origin_coord[0] / 2
    point[1] += origin_coord[1] / 2
    #stdscr.addstr(f"Point transform1: {point}\n")
    #2) Cambiar origen de sistema de coordenadas global
    point[0] += playfield_coord[0] / 2
    #point[1] += playfield_coord[1] / 2
    point[1] = playfield_coord[1] / 2 - point[1]
    #stdscr.addstr(f"Point transform2: {point}\n")
    #3) Cambiar escala de sistema de coordenadas -> calcular proporción y multiplicarla
    dw = win_coord[0] / playfield_coord[0]
    dh = win_coord[1] / playfield_coord[1]
    point[0] *= dw
    point[1] *= dh
    #point[0] = float_to_int(point[0])
    #point[1] = float_to_int(point[1])
    return point


def draw_game_frame(stdscr, config, frame):
    
    #stdscr.clear()
    stdscr.erase()
    curses.update_lines_cols()
    config["win_coord"] = [curses.COLS, curses.LINES]
    
    #check valid window size
    if curses.COLS <= MIN_W or curses.LINES <= MIN_H:
        error_msg = "ERROR: Invalid size to render game!"
        stdscr.addstr(error_msg[0:curses.COLS - 1])
        stdscr.refresh()
        return
    #calculate game space
    else:
        curr_ratio = curses.COLS / curses.LINES
        game_coord = config["win_coord"]
        if curr_ratio != ASPECT_RATIO:
            adjust_height_by_width = curses.COLS / ASPECT_RATIO
            adjust_width_by_height = curses.LINES * ASPECT_RATIO
            adjust_height_flag = False
            adjust_width_flag = False
            
            if adjust_height_by_width <= curses.LINES:
                adjust_height_flag = True
            if adjust_width_by_height <= curses.COLS:
                adjust_width_flag = True
            
            if adjust_height_flag and adjust_width_flag:
                rect1_area = curses.COLS * adjust_height_by_width
                rect2_area = curses.LINES * adjust_width_by_height
                if rect1_area > rect2_area:
                    game_coord = [curses.COLS, adjust_height_by_width]
                else:
                    game_coord = [adjust_width_by_height, curses.LINES]
            elif adjust_height_flag:
                game_coord = [curses.COLS, adjust_height_by_width]
            elif adjust_width_flag:
                game_coord = [adjust_width_by_height, curses.LINES]

        game_coord[0] *= 0.8
        game_coord[1] *= 0.8

    win_coord = config["win_coord"]
    playfield_coord = config["playfield_coord"]
    player_size = config["player_size"]
    ball_size = config["ball_size"]
    OFFSET_X = (win_coord[0] - game_coord[0]) / 2
    OFFSET_Y = (win_coord[1] - game_coord[1]) / 2

    ball = frame["Ball"]
    left_player = frame["Left_Player"]
    right_player = frame["Right_Player"]
    #transform ball and players point according to win coordinate system
    ball = transform_point(ball, ball_size, playfield_coord, game_coord)
    left_player = transform_point(left_player, player_size, playfield_coord, game_coord)
    right_player = transform_point(right_player, player_size, playfield_coord, game_coord)

    #transform ball and player vector size
    ball_size = point_transform_coordinates(ball_size, game_coord, playfield_coord)
    ball_size[0] = int(ball_size[0])
    ball_size[1] = int(ball_size[1])

    player_size = point_transform_coordinates(player_size, game_coord, playfield_coord)
    player_size[0] = int(player_size[0])
    player_size[1] = int(player_size[1])
    
    #add figures to stdscr buffer
    #ball
    ball_ly = int(ball[1] + OFFSET_Y)
    ball_lx = int(ball[0] + OFFSET_X)
    ball_ry = int(ball[1] + ball_size[1] + OFFSET_Y)
    ball_rx = int(ball[0] + ball_size[0] + OFFSET_X)
    rectangle(stdscr, ball_ly, ball_lx, ball_ry, ball_rx)
    #player1
    left_player_ly = int(left_player[1] + OFFSET_Y)
    left_player_lx = int(left_player[0] + OFFSET_X)
    left_player_ry = int(left_player[1] + player_size[1] + OFFSET_Y)
    left_player_rx = int(left_player[0] + player_size[0] + OFFSET_X)
    rectangle(stdscr, left_player_ly, left_player_lx, left_player_ry, left_player_rx)
    #player2
    right_player_ly = int(right_player[1] + OFFSET_Y)
    right_player_lx = int(right_player[0] + OFFSET_X)
    right_player_ry = int(right_player[1] + player_size[1] + OFFSET_Y)
    right_player_rx = int(right_player[0] + player_size[0] + OFFSET_X)
    rectangle(stdscr, right_player_ly, right_player_lx, right_player_ry, right_player_rx)
    
    #draw interface
    interface_y = int(curses.LINES * 0.05)
    player1_name = config["player1_name"]    
    player2_name = config["player2_name"]
    player1_x = int(curses.COLS * 0.1)
    player2_x = int(curses.COLS * 0.9 - len(player2_name))

    if frame["State"] == "golden goal":
        score = "golden goal"
        score_x = int(curses.COLS / 2 - len(score) / 2)
        stdscr.addstr(interface_y, score_x, score, curses.A_BOLD | curses.A_BLINK | curses.color_pair(2))
    else:
        score_info = frame["Score"]
        score = f"{score_info[0]} - {score_info[1]}"
        score_x = int(curses.COLS / 2 - len(score) / 2)
        stdscr.addstr(interface_y, score_x, score, curses.A_BOLD | curses.color_pair(1))
      
    stdscr.addstr(interface_y, player1_x, player1_name, curses.A_BOLD | curses.color_pair(1))
    #stdscr.addstr(interface_y, score_x, score, curses.A_BOLD | curses.color_pair(1))
    stdscr.addstr(interface_y, player2_x, player2_name, curses.A_BOLD | curses.color_pair(1))

    #draw playfield borders
    playfield_y = int(OFFSET_Y)
    playfield_x = int(OFFSET_X)
    playfield_h = int(game_coord[1] + OFFSET_Y - 0.5)
    playfield_w = int(game_coord[0] + OFFSET_X)
    rectangle(stdscr, playfield_y, playfield_x, playfield_h, playfield_w)
    #draw match timer
    if frame["Time"] >= 0:
        timer = str(int(frame["Time"]))
        timer_x = int(curses.COLS / 2 - len(timer) / 2)
        timer_y = int(curses.LINES * 0.95)
        if frame["Time"] <= 5:
            stdscr.addstr(timer_y, timer_x, timer, curses.A_BOLD | curses.A_BLINK | curses.color_pair(3))
        else:
            stdscr.addstr(timer_y, timer_x, timer, curses.A_BOLD | curses.color_pair(1))

    stdscr.refresh()

async def play_match(ws, type):
    response = await ws.recv()
    response_json = json.loads(response)
    if not "type" in response_json or response_json["type"] != "match_info":
        print("Not match info:", response_json)
        return False
    
    state = response_json["state"]
    curses.update_lines_cols()
    config = {
        "win_coord": [curses.COLS, curses.LINES],
        "playfield_coord": [state["playfield_w"], state["playfield_h"]],
        "player_size": [state["player_w"], state["player_h"]],
        "ball_size": [state["ball_side"], state["ball_side"]],
        "player1_name": "player1",
        "player2_name": "player2"
        }
    if type == "offline":
        config["player1_name"] = "player1"
        config["player2_name"] = "player2"
    if type == "online":
        config["player1_name"] = state["players_name"][0]
        config["player2_name"] = state["players_name"][1]

    while True:
        response = await ws.recv()
        response_json = json.loads(response)
        if response_json["type"] == "game_update":
            draw_game_frame(stdscr, config, response_json["state"])
            if response_json["state"]["State"] == "ended":
                break      
        await asyncio.sleep(0.005)
        
    response = await ws.recv()
    response_json = json.loads(response)
    if "type" in response_json:
        if response_json["type"] == "ended_match":
            return
        
async def play_offline_match(ws):
    await ws.send(json.dumps({
        "type": "join",
        "mode": "local"
    }))
    response = await ws.recv()
    response_json = json.loads(response)
    if not "type" in response_json or response_json["status"] != "success":
        print("Error creating match: ", response_json["code"])
        return False

    #init curses
    init_curses()
    #set inputs
    inputs_task = asyncio.create_task(inputs.offline_inputs(ws))
    await play_match(ws, "offline")

    #return terminal to normal state
    inputs_task.cancel()
    inputs.player1_input = None
    inputs.player2_input = None
    clean_curses()

async def play_online_match(ws):
    await ws.send(json.dumps({
        "type": "join",
        "mode": "online",
        "elo": 1000
    }))
    response = await ws.recv()
    response_json = json.loads(response)
    if not "type" in response_json or response_json["status"] != "success":
        print("Error sending matchmaking: ", response_json["code"])
        return False
    print("Waiting for another user to play online...")
    response = await ws.recv()
    response_json = json.loads(response)
    if not "type" in response_json or response_json["type"] != "accept_matchmaking":
        print("Matchmaking failed")
        return False
    
    init_curses()
    #set input task
    inputs_task = asyncio.create_task(inputs.online_inputs(ws))
    await play_match(ws, "online")
    #return terminal to normal state
    inputs_task.cancel()
    inputs.player1_input = None
    inputs.player2_input = None
    clean_curses()

async def select_game_mode(ws):
    
    while True:
        try:
            mode = input("SELECT GAME MODE: LOCAL OR ONLINE? OR EXIT TO CLOSE APP\n")
            if mode == "LOCAL":
                try:
                    await play_offline_match(ws)
                except KeyboardInterrupt:
                    return
                
            elif mode == "ONLINE":
                try:
                    await play_online_match(ws)
                except KeyboardInterrupt:
                    return
            elif mode == "EXIT":
                return
            else:
                print("No supported mode")
        except KeyboardInterrupt:
            return
        os.system("clear")

async def create_game_ws(jwt):
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    url = f"wss://localhost:4043/ws/game/?token={jwt}"
    try:
        ws = await websockets.connect(url, ssl=ssl_context)
    except Exception as e:
        print(e)
        return False
    return ws

def input_pwd():
    pwd = input("Password: ")
    repeat_pwd = input("Repeat password: ")
    if pwd != repeat_pwd:
        print("Password doesn't match")
        return False
    
    return pwd

def register():
    name = input("Name: ")
    pwd = input_pwd()
    while not pwd:
        pwd = input_pwd()
    url = "https://localhost:4043/auth_service/register/"
    try:
        response = requests.post(url, 
            json={"username": name,
                "password": pwd},
                verify=False
            #headers={"Content-Type": "application/json"}
            )
        json = response.json()
        if "error" in json:
            print("Error:", json["error"])
            return False
        return json["token"]
    except Exception:
        return False

    
def login():
    name = input("Name: ")
    pwd = input("Password: ")
    url = "https://localhost:4043/auth_service/login/"
    try:
        response = requests.post(url, 
            json={"username": name,
                "password": pwd},
                verify=False
            #headers={"Content-Type": "application/json"}
            )
        json = response.json()
        if "error" in json:
            print("Error:", json["error"])
            return False
        return json["token"]
    except Exception:
        return False


def enter_page():

    while True:
        try:
            access = input("LOGIN OR REGISTER? OR EXIT TO CLOSE APP\n")
            if access == "LOGIN":
                jwt = login()
            elif access == "REGISTER":
                jwt = register()
            elif access == "EXIT":
                exit(1)
            else:
                print("Unsupported operation. Try again.")
        except KeyboardInterrupt:
            exit(1)
        except EOFError:
            print("Ctrl-D")
        if jwt:
            return jwt
    
    
async def cli():
    jwt = enter_page()
    if not jwt:
        exit(1)
        
    ws = await create_game_ws(jwt)
    if not ws:
        exit(1)
    
    await select_game_mode(ws)
    
loop = asyncio.new_event_loop()   
asyncio.set_event_loop(loop)

def is_script_running(script_name):
    current_pid = os.getpid()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['pid'] == current_pid:
            continue
        if process.info['cmdline'] and script_name in process.info['cmdline']:
            return True
        
    return False

if __name__ == "__main__":
    if is_script_running("cli.py") == False:
        print('Welcome to the Pong CLI application!')
        atexit.register(clean_curses)
        loop.run_until_complete(cli())
    else:
        print('Pong CLI application already running in another terminal...')
