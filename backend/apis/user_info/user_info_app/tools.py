import requests
import json
from .models import UserInfo, MatchHistory
from django.http import HttpResponse, JsonResponse
from functools import wraps
from .enums import Elo_constant
from .consumers import connected_users
import re

MAX_LENGHT_USERNAME = 20


def get_user_name_from_token_request(request):
    verify_token_url = "http://auth_service:8000/verify_token/"
    auth_header = request.headers.get("Authorization")
    host_header = request.get_host()
    if not auth_header:
        return {"status": 400, "data": {"error": "Token not received"}}
    return get_user_name_from_token(auth_header, host_header)

def get_user_name_from_token(token, host):
    verify_token_url = "http://auth_service:8000/verify_token/"
    headers = {"Authorization": token, "Host": host}
    response = requests.get(verify_token_url, headers=headers)
    if not response.text.strip():
        return {
            "status": response.status_code,
            "data": {"error": "Empty response from verification service"},
        }
    try:
        response_data = response.json()
    except json.JSONDecodeError:
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

def get_user_info_tool(username):
    try:
        user_sql = UserInfo.objects.get(username=username)
    except UserInfo.DoesNotExist:
        return JsonResponse({"error": "Not registered"}, status=401)

    try:
        matches_as_opponent_1 = MatchHistory.objects.filter(opponent_1=user_sql)
        matches_as_opponent_2 = MatchHistory.objects.filter(opponent_2=user_sql)
        all_matches = matches_as_opponent_1 | matches_as_opponent_2
    except MatchHistory.DoesNotExist:
        return JsonResponse({"error": "No matches found"}, status=404)

    match_history = []
    for match in all_matches:
        match_info = {
            "opponent": (
                match.opponent_2.alias
                if match.opponent_1 == user_sql
                else match.opponent_1.alias
            ),
            "userPoints": (
                match.opponent_1_points
                if match.opponent_1 == user_sql
                else match.opponent_2_points
            ),
            "opponentPoints": (
                match.opponent_2_points
                if match.opponent_1 == user_sql
                else match.opponent_1_points
            ),
            "match_type": match.match_type,
            "elo_earn":  (
                match.elo_earned_opponent_1
                if match.opponent_1 == user_sql
                else match.elo_earned_opponent_2
            ),
            "date": match.date
        }
        match_history.append(match_info)
    
    all_users = UserInfo.objects.all().order_by('-elo')
    user_rank = list(all_users).index(user_sql) + 1

    user_data = {
        "alias": user_sql.alias,
        "status": is_user_online(user_sql.username),
        "elo": user_sql.elo,
        "photo_profile": user_sql.photo_profile,
        "wins": user_sql.wins,
        "loses": user_sql.loses,
        "ranking": user_rank,
        "cups": user_sql.cups,
        "matchHistory": match_history
    }
    return JsonResponse(user_data)


def get_oponent_usernames_from_match(opponent_1_jwt, opponent_2_jwt):

    opponent_1_username_response = get_user_from_jwt(opponent_1_jwt)
    if opponent_1_username_response["status"] != 200:
        return JsonResponse({"error": "oponent 1 jwt was not valid"}, status=400)
    opponent_2_username_response = get_user_from_jwt(opponent_2_jwt)
    if opponent_2_username_response["status"] != 200:
        return JsonResponse({"error": "oponent 2 jwt was not valid"}, status=400)
    return JsonResponse(
        {
            "status": 200,
            "data": {
                "opponent_1": opponent_1_username_response["data"]["username"],
                "opponent_2": opponent_2_username_response["data"]["username"],
            },
        }
    )


def parse_add_match_history_request(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    opponent_1_jwt = data.get("opponent_1_jwt")
    if not opponent_1_jwt:
        return JsonResponse({"error": "opponent 1 jwt is required"}, status=400)
    opponent_2_jwt = data.get("opponent_2_jwt")
    if not opponent_2_jwt:
        return JsonResponse({"error": "opponent 2 jwt is required"}, status=400)
    if not "opponent_1_points" in data:
        return JsonResponse({"error": "opponent 1 points is required"}, status=400)
    opponent_1_points = data["opponent_1_points"]
    if not "opponent_2_points" in data:
        return JsonResponse({"error": "opponent 2 points is required"}, status=400)
    opponent_2_points = data["opponent_2_points"]
    match_type = data.get("match_type")
    if not match_type:
        return JsonResponse({"error": "match_type is required"}, status=400)
    return JsonResponse(
        {
            "status": 200,
            "data": {
                "opponent_1_jwt": opponent_1_jwt,
                "opponent_2_jwt": opponent_2_jwt,
                "opponent_1_points": opponent_1_points,
                "opponent_2_points": opponent_2_points,
                "match_type": match_type,
            },
        }
    )


def calculate_elo_earned(opponent_1, opponent_2, opponent_1_points, opponent_2_points):
    Elo1 = opponent_1.elo
    Elo2 = opponent_2.elo
    Player1_win_prob = 1 / (1 + 10 ** ((Elo2 - Elo1) / float(Elo_constant.S)))
    Player2_win_prob = 1 / (1 + 10 ** ((Elo1 - Elo2) / float(Elo_constant.S)))
    Player1_potential_elo_gain = (
        int(float(Elo_constant.K) * (float(Elo_constant.W) - Player1_win_prob)) + 1
    )
    Player2_potential_elo_gain = (
        int(float(Elo_constant.K) * (float(Elo_constant.W) - Player2_win_prob)) + 1
    )
    
    if opponent_1_points > opponent_2_points:
        return {
            "opponent_1_earn": Player1_potential_elo_gain,
            "opponent_2_earn": Player1_potential_elo_gain * -1,
        }
    elif opponent_1_points < opponent_2_points:
        return {
            "opponent_1_earn": Player2_potential_elo_gain * -1,
            "opponent_2_earn": Player2_potential_elo_gain,
        }
    else:
        return {"opponent_1_earn": 0, "opponent_2_earn": 0}

def update_user_info_after_match(elo_calculated, opponent_1_model, opponent_2_model):
    if elo_calculated["opponent_1_earn"] != 0:
        try:
            opponent_1_model.elo = opponent_1_model.elo + elo_calculated["opponent_1_earn"]
            opponent_2_model.elo = opponent_2_model.elo + elo_calculated["opponent_2_earn"]
            if elo_calculated["opponent_1_earn"] > 0:
                opponent_1_model.wins = opponent_1_model.wins + 1
                opponent_2_model.loses = opponent_2_model.loses + 1
            if elo_calculated["opponent_1_earn"] < 0:
                opponent_2_model.wins = opponent_2_model.wins + 1
                opponent_1_model.loses = opponent_1_model.loses + 1
            opponent_1_model.save()
            opponent_2_model.save()
        except Exception as e:
            return JsonResponse({"error": e}, status=400)
    return JsonResponse({"opponent_1_earn": elo_calculated["opponent_1_earn"], "opponent_2_earn": elo_calculated["opponent_2_earn"]}, status=200)

def token_verification_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        verification_result = get_user_name_from_token_request(request)
        if verification_result["status"] != 200:
            return JsonResponse(
                verification_result["data"], status=verification_result["status"]
            )
        request.username = verification_result["data"].get("username")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def get_user_from_jwt(jwt):
    headers = {"Authorization": jwt, "Host": "localhost"}
    verify_token_url = "http://auth_service:8000/verify_token/"
    response = requests.get(verify_token_url, headers=headers)
    if not response.text.strip():
        return {
            "status": response.status_code,
            "data": {"error": "Empty response from verification service"},
        }
    try:
        response_data = response.json()
    except json.JSONDecodeError:
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


def is_user_online(username):
    if username in connected_users:
        return "Online"
    return "Offline"


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