import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)
users = {}
del_users = set()

def newUser(username, alias, token):
    global users
    users[username] = {
        "name": alias,
        "token": token,
        "state": "idle",
        "mode": None,
        "consumers": 1,
        "consumers_objs": [],
        "context": None
    }

def newSession(id, username):
    global sessions
    sessions[id] = {
        "id": id,
        "username": username
    }

def getUserEntry(name):
    global users
    if not name in users:
        return False
    return users[name]

async def updateUser(name, state, mode, context):
    global users
    if not name in users:
        return
    user = users[name]
    user["state"] = state
    user["mode"] = mode
    user["context"] = context

async def updateConsumer(consumer, state, mode, context):
    if not consumer:
        return 
    consumer.state = state
    consumer.mode = mode
    consumer.context = context

async def updateUserAttr(name, attr, value):
    if not name in users:
        return False
    user = user["name"]
    if not attr in user:
        return False
    user[attr] = value

def getUserAttr(name, attr):
    if not name in users:
        return False
    user = users[name]
    if not attr in user:
        return False
    return user[attr]

def filterUsersbyContext(users, key, value):

    match = []

    for user in users:
        context = user["context"]
        if type(context) == dict:
            if context[key] == value:
                match.append(user)

    return match

def updateUserState(name, state, state_info):
    global users
    user = users[name]
    user["state"] = state
    user["state_info"] = state_info


def updateUsers(state, room, *users):
    for user in users:
        user.state = state
        user.room = room

async def get_alias_from_token(token, host):
            
    verify_token_url = "http://user_info:8000/get_alias_from_token"
    headers = {"Authorization": token, "Host": host}

    async with httpx.AsyncClient() as client:
        response = await client.get(verify_token_url, headers=headers)

    if not response.text.strip():
        return {
            "status": response.status_code,
            "data": {"error": "Empty response from verification service"},
        }

    try:
        response_data = response.json()
    except httpx.JSONDecodeError:
        return {
            "status": response.status_code,
            "data": {"error": "Response not in JSON format"},
        }

    if response.status_code != 200:
        return {"status": response.status_code, "data": response_data}

    username = response_data.get("alias")
    if not username:
        return {"status": 400, "data": {"error": "Username not found in token"}}

    return {"status": 200, "data": {"alias": username}}

async def get_username_from_token(token, host):
            
    verify_token_url = "http://auth_service:8000/verify_token/"
    headers = {"Authorization": token, "Host": host}

    async with httpx.AsyncClient() as client:
        response = await client.get(verify_token_url, headers=headers)

    if not response.text.strip():
        return {
            "status": response.status_code,
            "data": {"error": "Empty response from verification service"},
        }
    try:
        response_data = response.json()
    except httpx.JSONDecodeError:
        return {
            "status": response.status_code,
            "data": {"error": "Response not in JSON format"},
        }

    if response.status_code != 200:
        return {"status": response.status_code, "data": response_data}

    username = response_data.get("username")
    if not username:
        return {"status": 400, "data": {"error": "Username not found in token"}}

    return {"status": 200, "data": {"username": username}}

def get_token_from_query_string(query_string):
    #get username
    params = dict(param.split('=') for param in query_string.split('&'))
    token = params.get('token')
    if not token:
        return False

    return token

async def checkUsers():
    global users
    global del_users

    while True:
        if del_users:
            idle_del_users = set(username for username, user in users.items() if username in del_users and user["state"] == "idle")
            users = {username:user for username, user in users.items() if username not in idle_del_users}
            del_users = set(username for username in users.keys() if username not in idle_del_users)
            logger.warning(f"Users after cleanup: {users}")
            logger.warning(f"del_users after cleanup: {del_users}")
        await asyncio.sleep(0.25) 