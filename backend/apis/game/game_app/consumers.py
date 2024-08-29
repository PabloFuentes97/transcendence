# game/consumers.py
import json
import time
import asyncio
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

from . import Matches, Tournaments, Users, Matchmaking
import logging

logger = logging.getLogger(__name__)

MAX_PLAYERS = 2

gameRooms = {}

#waitingPlayers = {}
waitingPlayers = []

flagInitServer = False


class GameConsumer(AsyncWebsocketConsumer):

    state = None
    mode = None
    match = None
    context = None
    jwt = None
    elo = None
    task = None
    alias = None
    #consumer connect
    async def connect(self):

        if flagInitServer == False:
            flagInitServer == True
            #asyncio.create_task(Tournaments.checkTournaments())
            asyncio.create_task(Matches.checkMatches())
            #asyncio.create_task(Users.checkUsers())
        self.state = "connecting"
        token = Users.get_token_from_query_string(self.scope['query_string'].decode('utf-8'))
        if not token:
            return
        self.jwt = token
        username_json = await Users.get_username_from_token(token, "localhost")
        if username_json["status"] != 200:
            return
        self.username = username_json["data"]["username"]
        alias_json = await Users.get_alias_from_token(token, "localhost")
        if alias_json["status"] != 200:
            return
        self.alias = alias_json["data"]["alias"]
        logger.warning(f"Username: {self.username}, Alias: {self.alias}, jwt: {self.jwt}")
        await self.accept()
        self.state = "idle"
        if not self.username in Users.users:
            logger.warning("User wasn't connected, add to Users list")
            Users.newUser(self.username, self.alias, token)
        else:
            logger.warning("User already added, increment number of consumers")
            Users.users[self.username]["consumers"] += 1

        Users.users[self.username]["consumers_objs"].append(self)

    #consumer disconnect
    async def disconnect(self, close_code):

        logger.warning("DISCONNECT")
        if self.state == "connecting":
            return
        if self.state == "active":
            logger.warning(f"Consumer in mode {self.mode}")
            if self.mode == "local" or self.mode == "online":
                await Matches.leaveMatch(self, Matches.matches[self.context])
            
            elif self.mode == "matchmaking":
                if self in Matchmaking.waitList:
                    Matchmaking.waitList.remove(self)
                elif self in Matchmaking.priorityList:
                    Matchmaking.priorityList.remove(self)
                task = self.context
                task.cancel()

            elif self.mode == "tournament":
                tournament = Tournaments.tournaments[self.context["tournamentName"]]
                await Tournaments.leaveTournament(tournament, self)
            
        #update User
        if self.state == "active":
            await Users.updateUser(self.username, "idle", None, None)
        user = Users.getUserEntry(self.username)
        user["consumers_objs"].remove(self)
        user["consumers"] -= 1
        if user["consumers"] == 0:
            logger.warning("No consumers left with same user, remove user from table")
            del Users.users[self.username]
            #Users.del_users.add(self.username)
            
    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except Exception as e:
            logger.warning(f"{e}")
            return 

        if not "type" in text_data_json:
            logger.warning("Error: not type in json")
            return
        
        type = text_data_json["type"]

        user = Users.getUserEntry(self.username)
        #join mode request
        if type == "join":

            logger.warning("JOIN")
            if user["state"] != "idle":
                logger.warning("Error: User already active!")
                await self.send(text_data=json.dumps(
                    {"type": "join", "status": "error", "code": "user already active"}
                    ))
                return
            
            if not "mode" in text_data_json:
                logger.warning("Error: not mode in json")
                await self.send(text_data=json.dumps(
                    {"type": "join", "status": "error", "code": "not 'mode' attribute in json"}
                    ))
                return
            
            await self.send(text_data=json.dumps(
                {"type": "join", "status": "success"}
                ))
            
            mode = text_data_json["mode"]
            logger.warning(f"MODE: {mode}")
            #join local match
            if mode == "local":
                matchName = f"{self.username}_local_match"
                if ' ' in matchName:
                    matchName = matchName.replace(' ', '')
                match = Matches.newMatch(matchName, "local", self)
                await Users.updateUser(self.username, "active", "local", matchName)
                await Users.updateConsumer(self, "active", "local", matchName)
                match["task"] = asyncio.create_task(Matches.runMatchTask(match))
                Matches.matches[matchName] = match
                await channel_layer.group_add(matchName, self.channel_name)

            #join online match -> enter matchmaking
            elif mode == "online":
                if not "elo" in text_data_json:
                    logger.warning("Not elo in JSON")
                    await self.send(text_data=json.dumps(
                        {"type": "join", "status": "error", "code": "not 'elo' attribute in json"}
                    ))
                    return
                self.elo = text_data_json["elo"]
                task = asyncio.create_task(Matchmaking.look_match(self))
                await Users.updateUser(self.username, "active", "matchmaking", task)
                await Users.updateConsumer(self, "active", "matchmaking", task)

            #join tournament -> enter queue
            elif mode == "tournament":
                logger.warning("Join tournament")
                await Tournaments.joinTournament(self)

        #leave active context
        elif type == "leave":
            logger.warning("LEAVE")
            user = Users.users[self.username]
            logger.warning(user)
            if user["state"] == "idle":
                logger.warning("Error: User is not active!")
                await self.send(text_data=json.dumps(
                    {"type": "leave", "status": "error", "code": "user not active"}
                    ))
                return
            
            if not "context" in text_data_json:
                logger.warning("Error: not 'context' in json")
                await self.send(text_data=json.dumps(
                    {"type": "leave", "status": "error", "code": "not 'context' attribute in json"}
                    ))
                return

            context = text_data_json["context"]
            logger.warning(f"CONTEXT: {context}")
            await self.send(text_data=json.dumps(
                    {"type": "leave", "status": "success"}
                    ))
            #leave match
            if context == "match":
                logger.warning(f"Leave match")
                if user["context"] in Matches.matches:
                    match = Matches.matches[user["context"]]
                    await Matches.leaveMatch(self, match)

            #leave matchmaking queue
            elif context == "matchmaking":
                logger.warning(f"User {self.username} left matchmaking")
                if self in Matchmaking.waitList:
                    Matchmaking.waitList.remove(self)
                elif self in Matchmaking.priorityList:
                    Matchmaking.priorityList.remove(self)
                task = user["context"]
                task.cancel()

            #leave tournament
            elif context == "tournament":
                tournament = Tournaments.tournaments[user["context"]["tournamentName"]]
                await Tournaments.leaveTournament(tournament, self)
            
            await Users.updateUser(self.username, "idle", None, None)
            await Users.updateConsumer(self, "idle", None, None)

        elif type == "update_input":
            user_state = Users.getUserEntry(self.username)["state"]
            if user_state != "idle":
                if not "mode" in text_data_json:
                    return
                input_mode = text_data_json["mode"]
                
                if input_mode == "offline":
                    match = Matches.matches[user["context"]]
                    if "0" in text_data_json:
                        Matches.updateInput(match, 0, text_data_json["0"])
                    if "1" in text_data_json:
                        Matches.updateInput(match, 1, text_data_json["1"])
                    
                elif input_mode == "online":
                    
                    user_mode = Users.getUserAttr(self.username, "mode")
                    if user_mode == "online":
                        match = Matches.matches[user["context"]]
                        idx = Matches.getUserInputIdx(match, self)
                        Matches.updateInput(match, idx, text_data_json["key"])

                    elif user_mode == "tournament":
                        context = user["context"]
                        match = Matches.matches[context["match"]]
                        idx = Matches.getUserInputIdx(match, self)
                        Matches.updateInput(match, idx, text_data_json["key"])

        elif type == "tournament_user_ready":
            context = Users.getUserAttr(self.username, "context")
            if not context:
                return
            context["ready"] = True

        elif type == "update_alias":
            if not "alias" in text_data_json:
                return
            new_alias = text_data_json["alias"]
            logger.warning(f"UPDATE ALIAS: {new_alias}")
            self.alias = new_alias
            Users.users[self.username]["alias"] = new_alias

        elif type == "log_out":
            await self.close(1000)
    
    # Send game state
    async def send_msg(self, event):
        message = event["msg"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps(
            message
            ))