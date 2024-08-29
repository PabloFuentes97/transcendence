import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import UserAuth
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
import os
import jwt
import logging
import pyotp
import re
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)
MAX_LENGHT_USERNAME = 20
MAX_LENGHT_PASSWORD = 20

@csrf_exempt
def get_access_token_from_intra(client_id, client_secret, code):
    """ Exchange authorization code for access token """
    url = 'https://api.intra.42.fr/oauth/token'
    payload = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': "http://auth_service/login_intra/"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()  # Returns JSON with access token
    except requests.exceptions.RequestException as e:
        # Handle request errors
        return {'error': 'Request failed', 'details': str(e)}


def get_info_from_intra_token(access_token):
    user_info_url = 'https://api.intra.42.fr/v2/me'
    user_info_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_info_response = requests.get(user_info_url, headers=user_info_headers)
    if user_info_response.status_code == 200:
        try:
            user_info = user_info_response.json()
            response_info = {
                'login_name' : user_info['login'],
                'profile_photo' : user_info['image']['versions']['medium']
            }
            return {'status_code': 200, 'response_info': response_info}
        except Exception as e:
            return {'status_code': 400, 'error': e}
    else:
        return {'status_code': 400, 'error': "error requesting to the 42 api"}
    

def register_user_from_intra(intra_info):
    try:
        intra_username = f'{intra_info["login_name"]}_intra'
        response_user_exist = user_exist_api_call(intra_username)
        if response_user_exist.status_code == 400:
            return response_user_exist
        jwt_token = create_jwt(intra_username)
        if response_user_exist.status_code == 200:
            response_create_user = create_user_api_call(intra_username, intra_info["profile_photo"], intra_info["login_name"], jwt_token)
            if response_create_user.status_code != 200:
                return response_create_user
            new_user = UserAuth(
                    username=intra_username,
                    password=jwt_token,
                    is_from_intra=True)
            new_user.save()
        return {'status_code': 200, 'token': jwt_token, 'username': intra_username}
    except Exception as e:
        return {'status_code': 400, 'error': e}


def get_token_from_intra(request):
    client_id = os.environ.get("INTRA_UID")
    client_secret = os.environ.get("INTRA_SECRET_KEY")
    localhost = os.environ.get("LOCALHOST")
    code = request.GET.get('code')
    if code:
        url = 'https://api.intra.42.fr/oauth/token'
        payload = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': f"https://{localhost}:4043/auth_service/login_intra/"
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        return requests.post(url, data=payload, headers=headers)
    else:
        return JsonResponse({'error': "no code in return to intra"}, status=400)
    
def user_exist_api_call(username):
    exist_user_url = "http://user_info:8000/exist_user"
    headers_exist_user = {
    'Host': "localhost"
    }
    params = {
        "username": username
    }
    return requests.get(exist_user_url, headers=headers_exist_user, params=params)

def create_user_api_call(username, profile_photo, login_name, jwt_token):
    create_user_url = "http://user_info:8000/create_user_info"
    headers_create_user = {
        'Host': "localhost",
        'Authorization': jwt_token
    }
    alias_exist_url = "http://user_info:8000/exist_alias"
    params_alias_exist = {
        "alias": login_name
    }
    response_alias_exist = requests.get(alias_exist_url, headers=headers_create_user, params=params_alias_exist)
    alias = username
    if response_alias_exist.status_code == 200:
        alias = login_name
    body_create_user = {
        'username': username,
        'alias': alias,
        'profile_photo': profile_photo
    }
    return requests.post(url=create_user_url, headers=headers_create_user, json=body_create_user)


def create_jwt(username):
    payload = {
                'username': username,
                'exp': datetime.utcnow() + timedelta(days=1)
            }
    return jwt.encode(payload, os.environ.get("SECRET_JWT"), algorithm='HS256')

def delete_user_auth(username):
    try:
        user_selected = UserAuth.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=404)
    user_selected.delete()
    return JsonResponse({'deleted': 'user deleted'}, status=200)
  

def is_valid_username(username):
    username_regex = re.compile(r'^[a-zA-Z0-9_-]+$')
    if not username_regex.match(username):
        return False, 'use only alphanumeric values or _ -'
    if ' ' in username:
        return False,  'there shoud not be spaces in the username'
    if len(username) > MAX_LENGHT_USERNAME:
        return False, 'username should be shorter than 15 characters'
    if username.endswith('_intra'):
        return False, "Username cannot end with '_intra'."
    return True, "valid username"

def error_2fa_code(code):
    if not code.isnumeric():
        return False
    if len(code) > 8:
        return False
    return True

def is_2fa_code_valid(code, user_selected):
    try:
        otp = pyotp.TOTP(user_selected.key_2fa)
    except Exception:
        return False
    if not otp.verify(code):
        return False
    return True

def alias_exist_user_info(username):
    alias_exist_url = "http://user_info:8000/exist_alias"
    params_alias_exist = {
        "alias": username
    }
    headers_create_user = {
        'Host': "localhost"
    }
    response_alias_exist = requests.get(alias_exist_url, headers=headers_create_user, params=params_alias_exist)
    if response_alias_exist.status_code == 200:
        return False
    return True