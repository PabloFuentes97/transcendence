import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import httpx
import logging

connected_users = []
logger = logging.getLogger(__name__)

class LoginConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        params = dict(param.split('=') for param in query_string.split('&'))
        token = params.get('token')
        if not token or token == "null":
            logger.warning("Token null")
            await self.close()
            return
        response_username = await get_user_name_from_token_from_ws(token, "localhost")
        if response_username["status"] != 200:
            await self.close()
            return
        try:
            self.username = response_username["data"]["username"]
            if not self.username in connected_users:
                connected_users.append(self.username)
            await self.accept()
        except Exception as e:
            await self.close()
            return


    async def disconnect(self, close_code):
        try:
            if self.username and hasattr(self, 'username') :
                connected_users.remove(self.username)
        except Exception:
            return



    async def receive(self, text_data):
        # Handle incoming messages here
        pass

async def get_user_name_from_token_from_ws(token, host):
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