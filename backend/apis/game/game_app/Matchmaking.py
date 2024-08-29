from . import Users, Matches
import asyncio
from channels.layers import get_channel_layer
import logging
import time
from typing import Any, Awaitable

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

firstCheck = []
waitList = []
priorityList = []

FIRST_CHECK_SLEEP = 5
PRIORITY_TIME = 15

matchmakingTask = None


async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)


async def joinUsers(user1, user2):
    logger.warning("Create match from matchmaking")
    
    matchName = f"{user1.username}_{user2.username}"
    if ' ' in matchName:
        matchName = matchName.replace(' ', '')
    await Users.updateUser(user1.username, "active", "online", matchName)
    await Users.updateConsumer(user1, "active", "online", matchName)
    await Users.updateUser(user2.username, "active", "online", matchName)
    await Users.updateConsumer(user2, "active", "online", matchName)
    '''
    Users.updateConsumer(user1, "playing", matchName)
    Users.updateConsumer(user2, "playing", matchName)
    user1.mode = "online"
    user2.mode = "online"
    '''
    await channel_layer.group_add(matchName, user1.channel_name)
    await channel_layer.group_add(matchName, user2.channel_name)
    await channel_layer.group_send(matchName, {
        "type": "send.msg", "msg":
        {
            "type": "accept_matchmaking",
            "room_name": matchName,
            "player1": user1.username,
            "player2": user2.username
        }
    })
    match = Matches.newMatch(matchName, "online", user1, user2)
    match["task"] = asyncio.create_task(Matches.runMatchTask(match))
    Matches.matches[matchName] = match

def compareElo(user1_elo, user2_elo):
    return True if (abs(user1_elo - user2_elo) <= 50) else False

def nearestElo(self):
    if len(priorityList) == 1:
        return priorityList[0]
    
    nearest = priorityList[0]
    for waiting in priorityList[1:]:
        if (abs(waiting.elo - self.elo) < nearest.elo):
            nearest = waiting
    return nearest

async def addToPriorityLst(user):
    await asyncio.sleep(15)
    if user in waitList:
        logger.warning("Didn't find match in limit time, search in priorityList")
        waitList.remove(user)
        if priorityList:
            nearest = nearestElo(user)
            logger.warning(f"Nearest user: {nearest.username}")
            priorityList.remove(nearest)
            await joinUsers(user, nearest)
    else:
        logger.warning("Priority list is empty, add to priority list")
        priorityList.append(user)
    
async def look_match(self):
    await asyncio.sleep(5)
    #plantear esto en un while True, que checkee cada x tiempo si consigue encontrar a alguien
    if priorityList:
        logger.warning(f"Check priorityList")
        nearest = nearestElo(self)
        logger.warning(f"Nearest user: {nearest.username}")
        priorityList.remove(nearest)
        await joinUsers(self, nearest)
        return

    foundUser = None
    for waiting in waitList:
        logger.warning(f"Check {waiting.username} in waitList")
        if compareElo(self.elo, waiting.elo) == True:
            logger.warning("They match!")
            #await joinUsers(self, waiting)
            foundUser = waiting
            break
    
    if foundUser:
        waitList.remove(foundUser)
        await joinUsers(self, foundUser)
        return
     
    logger.warning(f"Add {self.username} to waitLst")    
    waitList.append(self)

    #asyncio.create_task(addToPriorityLst(self))
    await asyncio.sleep(15)
    if self in waitList:
        logger.warning("Didn't find match in limit time, search in priorityList")
        
        if priorityList:
            nearest = nearestElo(self)
            logger.warning(f"Nearest user found: {nearest.username}")
            priorityList.remove(nearest)
            await joinUsers(self, nearest)
        else:
            logger.warning("Priority list is empty, add to priority list")
            priorityList.append(self)
        waitList.remove(self)
