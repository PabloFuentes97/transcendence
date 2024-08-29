import asyncio
from . import Matches, Users
import logging
import math
import time
import json
import httpx
import os
from dotenv import load_dotenv
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

load_dotenv()
PASSWORD = os.environ["SERVICE_PASSWORD"]
logger = logging.getLogger(__name__)

tournaments = {}
tournamentsIdx = 0

TOURNAMENT_MAX_PLAYERS = 4
TOURNAMENT_MAX_ROUNDS = 2

def newTournament():
    global tournamentsIdx
    tournamentsIdx += 1

    tournament = {
        "name": f"tournament_{tournamentsIdx}",
        "users": {},
        "del_users": {},
        "rounds": {},
        "curr_round": 0,
        "state": "initializing",
        "winner": None,
        "task": None
    }
    return tournament
    
    
def findAvailableTournament():
    if len(tournaments) == 0:
        return None
    last = next(reversed(tournaments.values()))
    if last["state"] == "running":
        return None
    return last

async def joinTournament(user):
    
    tournamentName = None
    tournament = findAvailableTournament()
    if not tournament:
        tournament = newTournament()
        tournament["users"][user.username] = {"username": user.username, "alias": user.alias, "consumer": user}
        tournamentName = f"tournament_{tournamentsIdx}"
        tournaments[tournamentName] = tournament
        await channel_layer.group_add(tournamentName, user.channel_name)
        await channel_layer.group_send(tournamentName, {"type": "send.msg", "msg": {
                "type": "tournament_players_queue",
                "players_n": len(tournament["users"])
        }})
        logger.warning(f"New tournament created: {tournamentName}")
        logger.warning(f"User {user.username} added to tournament {tournamentName}")
    else:
        users = tournament["users"]
        users[user.username] = {"username": user.username, "alias": user.alias, "consumer": user}
        tournamentName = tournament["name"]
        logger.warning(f"User {user.username} added to tournament {tournamentName}")
        if len(users) == TOURNAMENT_MAX_PLAYERS:
            await channel_layer.group_add(tournamentName, user.channel_name)
            #await channel_layer.group_send(tournamentName, {"type": "send_msg", "msg": tournament}) #cambiarlo a json correcto
            tournament["task"] = asyncio.create_task(runTournamentTask(tournament))
        else:
            await channel_layer.group_add(tournamentName, user.channel_name)
            await channel_layer.group_send(tournamentName, {"type": "send.msg", "msg": {
                "type": "tournament_players_queue",
                "players_n": len(users)
            }})
    
    #user.room_name = tournament["name"]
    #user.state = "tournament"
    await Users.updateUser(user.username, "active", "tournament", {
        "tournamentName": tournamentName,
        "match": None,
        "ready": True,
    })
    await Users.updateConsumer(user, "active", "tournament", {
        "tournamentName": tournamentName,
        "match": None,
        "ready": True,
    })


async def leaveTournament(tournament, user):
    
    if tournament["state"] == "initializing":
        if user.username in tournament["users"]:
            del tournament["users"][user.username]
            await channel_layer.group_send(tournament["name"], {"type": "send.msg", "msg": {
                "type": "tournament_players_queue",
                "players_n": len(tournament["users"])
            }})

    elif tournament["state"] == "running":
        context = Users.users[user.username]["context"]
        if context["match"]:
            await Matches.leaveMatch(user, Matches.matches[context["match"]])
        else:
            tournament["del_users"][user.username] = {
                "name": user.username,
                "timestamp": time.time() * 1000
            }
        
    await channel_layer.group_discard(tournament["name"], user.channel_name)
    await Users.updateUser(user.username, "idle", None, None)
    await Users.updateConsumer(user, "idle", None, None)
    logger.warning(f"User {user.username} left tournament")

async def newRound(tournament, round_n, matches_idx, users):
    
    matches = []
    logger.warning(f"Players in round: {users}, len: {len(users)}")
    #winners = [None] * int(len(users) / 2)
    del_users = tournament["del_users"]
    logger.warning(f"CREATE NEW ROUND {round_n}")
    logger.warning(f"Players to create round: {users}")
    match_idx = 0
    users_keys = [*users]
    for i in range(0, len(users_keys), 2):

        user1 = users[users_keys[i]]
        user2 = users[users_keys[i + 1]]
        #check if player is in del_player or has already abandoned
        if (user1["username"] in del_users) or (user2["username"] in del_users):
            winner_alias = None
            if (user1["username"] in del_users) and (user2["username"] in del_users):
                logger.warning(f"Players {i} and {i + 1} are not available, winner is user to left first...")
                del_player1 = del_users[user1["username"]]
                del_player2 = del_users[user2["username"]]
                if del_player1["timestamp"] > del_player2["timestamp"]:
                    #winners[match_idx] = user2
                    del users[users_keys[i]]
                    winner_alias = user2["alias"]
                    del del_users[user1["username"]]
                    logger.warning(f"User {user2['alias']} is the winner, left after {user1['alias']}")
                else:
                    #winners[match_idx] = user1
                    del users[users_keys[i + 1]]
                    winner_alias = user1["alias"]
                    del del_users[user2["username"]]
                    logger.warning(f"User {user1['alias']} is the winner, left after {user2['alias']}")
            
            elif user1["username"] in del_users:
                logger.warning(f"Player {i} is not available, player {i + 1} directly wins!")
                #winners[match_idx] = user2
                del users[users_keys[i]]
                winner_alias = user2["alias"]
                player_context = Users.getUserAttr(user2["username"], "context")
                player_context["ready"] = True
                del del_users[user1["username"]]

            elif user2["username"] in del_users:
                logger.warning(f"Player {i + 1} is not available, player {i} directly wins!")
                #winners[match_idx] = user1
                del users[users_keys[i + 1]]
                winner_alias = user1["alias"]
                player_context = Users.getUserAttr(user1["username"], "context")
                player_context["ready"] = True
                del del_users[user2["username"]]

            await channel_layer.group_send(tournament["name"], {"type": "send.msg", "msg": {
                        "type": "tournament_match_ended",
                        "winner": winner_alias,
                        "match_id": match_idx + matches_idx
                }})    

        else: 
            matchname = f"{tournament['name']}_round_{round_n}_{user1['username']}_{user2['username']}"
            if ' ' in matchname:
                matchname = matchname.replace(' ', '')
            player1_context = Users.getUserAttr(user1["username"], "context")
            player1_context["match"] = matchname
            player2_context = Users.getUserAttr(user2["username"], "context")
            player2_context["match"] = matchname
            match = Matches.newMatch(matchname, "tournament", user1["consumer"], user2["consumer"])
            match["task"] = asyncio.create_task(Matches.runMatchTask(match))
            matches.append((match_idx, match))
            Matches.matches[matchname] = match
            await channel_layer.group_add(matchname, user1["consumer"].channel_name)
            await channel_layer.group_add(matchname, user2["consumer"].channel_name)

        match_idx += 1

    round = {
        "users": users,
        "matches": matches,
        #"winners": winners,
    }
    logger.warning(f"ROUND {round_n} CREATED!")
    return round


async def sendAsyncJsonRequest(url, headers, data):

    logger.warning("Send tournament winner to Users API")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            if response.status_code != 200:
                logger.warning("Request failed!")
                return
            try:
                resp_json = response.json()
            except Exception:
                logger.warning("Json failed!")

            return resp_json

        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url}")


async def runTournamentTask(tournament):
    tournamentName = tournament["name"]
    logger.warning(f"Starting tournament {tournamentName}...")
    logger.warning(f"Users: {tournament['users']}")
    tournament["state"] = "running"
    await channel_layer.group_send(tournamentName, {"type": "send.msg", "msg": {
                    "type": "init_tournament",
                    "players": [user["alias"] for username, user in tournament["users"].items()]
    }})
    del_users = tournament["del_users"]
    round_players = tournament["users"]
    #winners = []
    matches_idx = 0

    for round_n in range(0, TOURNAMENT_MAX_ROUNDS):
        active_users = [*round_players]
        #check if all active players are already ready to init round
        active_users_entries = [Users.getUserEntry(user) for user in active_users]
        all_ready_flag = False
        #check if players are ready or if they left
        while all_ready_flag == False:
            #checkear dentro si algun jugador se ha salido y esta en del_users -> en vez de borrarlo de la lista, lo cambio a "abandoned"
            if del_users:
                active_users = [user for user in active_users if user not in del_users]
            active_users_entries = [Users.getUserEntry(user) for user in active_users]
            all_ready = Users.filterUsersbyContext(active_users_entries, "ready", True)
            if len(all_ready) == len(active_users):
                all_ready_flag = True
                break
            await asyncio.sleep(0.01)

        await channel_layer.group_send(tournamentName, {"type": "send.msg", "msg": {
                    "type": "tournament_round_countdown"
        }})

        if not active_users:
            logger.warning("All players left. Tournament ended")
            return

        await asyncio.sleep(10)
        if del_users:
            active_users = [user for user in active_users if user not in del_users]
        if not active_users:
            logger.warning("All players left. Tournament ended")
            return

        #create new round
        round = await newRound(tournament, round_n, matches_idx, round_players)
        round_players = round["users"]
        logger.warning(f"Users in round: {round_players}")
        round_matches = round["matches"]
        for idx, match in round_matches:
            match_users = match["users"]
            for user in match_users:
                await user.send(text_data=json.dumps({
                    "type": "tournament_round_begin"
                }))
        tournament["rounds"][round_n] = round
        logger.warning(f"Round {round_n} starts...")
        end_matches = set()
        while round_matches:

            for idx, match in round_matches:
                task = match["task"]
                if task.done():
                    result = task.result()
                    winner = result["winner"]
                    loser = result["loser"]
                    logger.warning(f"Match {idx + matches_idx} ended")
                    if loser:
                        #logger.warning(f"LOSER: {loser}")
                        #logger.warning(f"Match loser: {Users.getUserEntry(loser.username)}")
                        await Users.updateUser(loser.username, "idle", None, None)
                        await Users.updateConsumer(loser, "idle", None, None)
                        await channel_layer.group_discard(tournamentName, loser.channel_name)
                    if winner:
                        #logger.warning(f"WINNER: {winner}")
                        #logger.warning(f"Winner: {Users.getUserEntry(winner.username)}")
                        winner_context = Users.getUserAttr(winner.username, "context")
                        if winner_context:
                            winner_context["match"] = None
                            winner_context["ready"] = False
            
                    await channel_layer.group_send(tournamentName, {"type": "send.msg", "msg": {
                        "type": "tournament_match_ended",
                        "winner": result["winner_alias"],
                        "match_id": idx + matches_idx
                    }})
                    end_matches.add(idx)
                    del round_players[result["loser_username"]]
                
            if end_matches:
                round_matches = tuple((idx, match) for idx, match in round_matches if idx not in end_matches)
                end_matches.clear()
            await asyncio.sleep(0.01) 

        logger.warning("All round matches ended!")
        matches_idx += len(round_players)
        #round_players = winners

    #tournament ended
    winner_key = [*round_players][0]
    winner = round_players[winner_key]
    logger.warning(f"Tournament ended, winner: {winner['alias']}")
    await Users.updateUser(winner["username"], "idle", None, None)
    await Users.updateConsumer(winner["consumer"], "idle", None, None)
    await sendAsyncJsonRequest("http://user_info:8000/add_cup_winner", {
        "host": "localhost", "Authorization": Users.getUserAttr(winner_key, "token")
        },
        {
          "password": PASSWORD,
        })
    await channel_layer.group_send(tournamentName, {"type": "send.msg", "msg": {
        "type": "tournament_ended",
        "winner": winner["alias"],
        "status": "success"
    }})

async def checkTournaments():

    global tournaments
    del_tournaments = set()
    while True:
        for tournamentName, tournament in tournaments.items():
            task = tournament["task"]
            if task and task.done():
                logger.warning(f"Match task {tournamentName} ended")
                del_tournaments.add(tournamentName)         

        if del_tournaments:
            tournaments = {tournamentName:tournament for tournamentName, tournament in tournaments.items() if tournamentName not in del_tournaments}
            del_tournaments.clear()

        await asyncio.sleep(0.25)