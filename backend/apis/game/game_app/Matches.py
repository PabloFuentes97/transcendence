import time
import random
import asyncio
import httpx
import logging
import json
from datetime import datetime

from typing import Any, Awaitable
from . import Users, Game

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

logger = logging.getLogger(__name__)

matches = dict()
del_matches = set()
endedMatches = {}
#endedMatches = set()
addMatches = []

frames = ()

MAXTIME = 5
MAXPOINTS = 10
PLAYERS_MAX = 2

#nombre de matches a borrar
ended_matches = []

def newMatch(name, type, *users):
    #borrar información que ya venga en el juego, es redundante
    match = {
        "name": name, 
        "users": list(users),
        "score": [0, 0],
        "winner": None,
        "inputs": [0 , 0],
        "state": "playing",
        "type": type, 
        "game": Game.game()
    }

    return match

def frameInfo(match):

    game = match["game"]
    game.update_frame(match["inputs"][0], match["inputs"][1])
    game_state = game.get_frame_info()
    match["inputs"] = ["", ""]
    #game_state["type"] = "game_update"
    match["score"] = game_state["Score"]
    #match["state"] = game_state["state"]
    #logger.warning("Hace frameInfo")
    return game_state

def getUserInputIdx(match, user):
    playerIdx = match["users"].index(user)
    return playerIdx

def updateInput(match, userIdx, input):
    match["inputs"][userIdx] = input 

async def sendResult(match):
    logger.warning("Send result to Users API")
    result_data = {
        "opponent_1_jwt": match["users"][0].jwt,
        "opponent_2_jwt": match["users"][1].jwt,
        "opponent_1_points": match["score"][0],
        "opponent_2_points": match["score"][1],
        "match_type": match["type"]
    }
    logger.warning(result_data)
    async with httpx.AsyncClient() as client:
        try:
            url = 'http://user_info:8000/add_match_history'
            response = await client.post(url, json=result_data, headers={
                "host": "localhost"
            })
            if response.status_code != 200:
                logger.warning("Hubo un error al enviar el resultado")
                return 
            else:
                logger.warning("Solicitud de enviar resultado funcionó bien!")
            try:
                resp_json = response.json()
            except Exception:
                logger.warning("Json failed!")

            return resp_json

        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url}")

async def endMatch(match):
    matchName = match["name"]
    logger.warning("MATCH ENDED")
    if match["type"] != "local":
        winnerIdx = 0 if match["score"][0] > match["score"][1] else 1
        loserIdx = 1 if match["score"][0] > match["score"][1] else 0
        match["winner"] = match["users"][winnerIdx]
        match["loser"] = match["users"][loserIdx]
        match["winner_alias"] = match["alias_names"][winnerIdx]
        match["winner_username"] = match["usernames"][winnerIdx]
        match["loser_alias"] = match["alias_names"][loserIdx]
        match["loser_username"] = match["usernames"][loserIdx]
    else:
        match["winner"] = "player1" if match["score"][0] > match["score"][1] else "player2"

    users = match["users"]
    
    ended_match_msg = {
            "type": "ended_match",
            "mode": match["type"],
            "players": [user.alias for user in match["users"]],
            "score": match["score"]
    }

    if match["type"] != "local":
        users_history = await sendResult(match)
        result_player = [None, None]
        if match["score"][0] > match["score"][1]:
            result_player[0] = "winner"
            result_player[1] = "defeat"
        else:
            result_player[0] = "defeat"
            result_player[1] = "winner"
        players_elo = [users_history["opponent_1_earn"], users_history["opponent_2_earn"]]
        logger.warning(players_elo)
        for idx, user in enumerate(users):
            ended_match_msg["elo_earned"] = players_elo[idx]
            ended_match_msg["result"] = result_player[idx]
            await user.send(text_data=json.dumps(
                ended_match_msg
            ))
    else:
        await channel_layer.group_send(matchName, {"type": "send.msg", "msg": ended_match_msg})
    
    if match["type"] != "tournament":
        for user_consumer in users:
            await Users.updateUser(user_consumer.username, "idle", None, None)
            await Users.updateConsumer(user_consumer, "idle", None, None)

    for user in users:
        await channel_layer.group_discard(matchName, user.channel_name)

async def runMatchTask(match):
    #tiempo de espera para que front muestre pantalla de arranque
    match["alias_names"] = [user.alias for user in match["users"]]
    match["usernames"] = [user.username for user in match["users"]]
    await asyncio.sleep(0.25)
    logger.warning(f"Match starts...")
    matchName = match["name"]
    await channel_layer.group_send(
                matchName, {"type": "send.msg", "msg": {
                    "type": "match_info", "state": 
                    {
                        "duration": Game.TIMELIMIT,
                        "playfield_w": Game.SCREEN_WIDTH,
                        "playfield_h": Game.SCREEN_HEIGHT,
                        "players_name": [user.alias for user in match["users"]],
                        "player_w": Game.Player.PLAYER_WIDTH,
                        "player_h": Game.Player.PLAYER_HEIGHT,
                        "ball_side": Game.Ball.SIDE_LEN,
                        "match_type": match["type"]
                    }}}
        )
    init_time = time.time()
    curr_time = init_time
    while curr_time < init_time + 3:
        if match["game"].state == "ended":
            await endMatch(match)
            return {
                "score": match["score"],
                "players": match["users"],
                "winner": match["winner"],
                "loser": match["loser"],
                "loser_username": match["loser_username"],
                "winner_username": match["winner_username"],
                "loser_alias": match["loser_alias"],
                "winner_alias": match["winner_alias"]
            }
        curr_time = time.time()
        await asyncio.sleep(0.01)
    
    #await asyncio.sleep(3)
    while match["game"].state != "ended":

        curr_time = time.time()
        frame = frameInfo(match)
        date = time.time()
        await channel_layer.group_send(
                matchName, {"type": "send.msg", "msg": {
                "type": "game_update", "state": frame, "timestamp": date}}
        )
        time_to_send = time.time() - curr_time
        if time_to_send > 16:
            time_to_sleep = 0.00005
        else:
            time_to_sleep = 0.016 - time_to_send - 0.002
            if time_to_sleep <= 0:
                time_to_sleep = 0.0000
        await asyncio.sleep(time_to_sleep)

    await endMatch(match)
    return {
        "score": match["score"],
        "players": match["users"],
        "winner": match["winner"],
        "loser": match["loser"],
        "loser_username": match["loser_username"],
        "winner_username": match["winner_username"],
        "loser_alias": match["loser_alias"],
        "winner_alias": match["winner_alias"]
    }

async def checkMatches():

    global del_matches
    global matches

    while True:
        #logger.warning("Checkear partidas")
        # logger.warning(f"Número de partidas: {len(matches)}")
        for matchName, match in matches.items():
            task = match["task"]
            if task.done():
                logger.warning(f"Match task {matchName} ended")
                del_matches.add(matchName)         

        if del_matches:
            matches = {matchName:match for matchName, match in matches.items() if matchName not in del_matches}
            del_matches.clear()

        await asyncio.sleep(0.25)

async def leaveMatch(consumer, match):
    #matchName = consumer.group_room_name
    #match = matches[matchName]
    if match["type"] != "local":
        userIdx = match["users"].index(consumer)
        rivalUserIdx = 0 if userIdx == 1 else 1
        match["score"][rivalUserIdx] = 3
        match["score"][userIdx] = 0
    #match["winner"] = match["users"][rivalUserIdx]
    #match["task"].cancel()
    match["game"].state = "ended"
