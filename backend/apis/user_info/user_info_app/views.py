from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .consumers import connected_users
from .enums import Profile_photo_options
from .tools import (
    get_user_info_tool,
    parse_add_match_history_request,
    token_verification_decorator,
    get_oponent_usernames_from_match,
    calculate_elo_earned,
    update_user_info_after_match,
    is_user_online,
    is_valid_username
)
from .models import UserInfo, MatchHistory, FriendRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import AnonymousUser
import json
import base64
import logging
import os
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv



load_dotenv()
logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_user_info(request):
    username = request.GET.get("username")
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)
    return get_user_info_tool(username)


@token_verification_decorator
@require_http_methods(["GET"])
def get_my_user_info(request):
    username = request.username
    return get_user_info_tool(username)


@token_verification_decorator
@require_http_methods(["GET"])
def get_user_info_from_alias(request):
    try:
        alias = request.GET.get("alias")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    try:
        user = UserInfo.objects.get(alias=alias)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Alias not found"}, status=404)
    return get_user_info_tool(user.username)


@token_verification_decorator
@require_http_methods(["GET"])
def get_all_users_info(request):
    try:
        order_by = request.GET.get('order_by')
        
        if order_by == 'elo':
            all_users = UserInfo.objects.all().order_by('-elo')
        else:
            all_users = UserInfo.objects.all().order_by('username')
    except ObjectDoesNotExist:
        return JsonResponse({"error": "No users found"}, status=404)
    
    limit = request.GET.get('limit')
    if limit:
        try:
            limit = int(limit)
            all_users = all_users[:limit]
        except ValueError:
            return JsonResponse({"error": "Invalid limit parameter"}, status=400)
    
    users_data = []
    for index, user in enumerate(all_users):
        user_dict = {
            "alias": user.alias,
            "status": is_user_online(user.username),
            "photo_profile": user.photo_profile,
            "elo": user.elo,
            "wins": user.wins
        }
        if order_by == 'elo':
            user_dict["ranking"] = index + 1
        users_data.append(user_dict)
    
    return JsonResponse({"users": users_data})


@token_verification_decorator
@require_http_methods(["POST"])
def create_user_info(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    username = data.get("username")
    if not username:
        return JsonResponse({"error": "username is required"}, status=400)
    exist = UserInfo.objects.filter(username=username).exists()
    if exist:
        return JsonResponse({"error": "Username already taken."}, status=400)
    alias = data.get("alias")
    if not alias:
        alias = username
    logger.warning("trying to create " + username)
    if not username.endswith('_intra'):
        is_valid, message_valid_username = is_valid_username(alias)
        if not is_valid:
            return JsonResponse({'error': message_valid_username }, status=400)
    exist = UserInfo.objects.filter(alias=alias).exists()
    if exist:
        return JsonResponse({"error": "Alias already taken."}, status=400)
    profile_photo = data.get("profile_photo")
    if not profile_photo:
        profile_photo = Profile_photo_options.DEFAULT
    new_user = UserInfo.objects.create(
        username=username, alias=alias, photo_profile=profile_photo
    )
    new_user.save()
    return JsonResponse({"Correct": "new user info created"}, status=200)


@token_verification_decorator
@require_http_methods(["POST"])
def upload_profile_photo(request):
    username = request.username
    try:
        file = request.FILES["file"]
    except KeyError:
        return JsonResponse({"error": "file is required"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"{e}"}, status=400)
    try:
        image = Image.open(file)
        image.verify()
        file.seek(0)
    except (IOError, SyntaxError) as e:
        return JsonResponse({"error": "Uploaded file is not a valid image"}, status=400)
    try:
        user_info_model = UserInfo.objects.get(username=username)
        if user_info_model.photo_profile:
            if user_info_model.photo_profile != Profile_photo_options.DEFAULT:
                existing_file_path = f"/usr/src/app{user_info_model.photo_profile}"
                if os.path.exists(existing_file_path):
                    os.remove(existing_file_path)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=401)
    try:
        file_extension = os.path.splitext(file.name)[1]
        file_name = f"{username}{file_extension}"
        file_path = f"/usr/src/app/profile_photos/{file_name}"
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        user_info_model.photo_profile = f"/profile_photos/{file_name}"
        user_info_model.save(update_fields=["photo_profile"])
    except Exception as e:
        return JsonResponse({"error": f"{e}"}, status=400)
    return JsonResponse({"Correct": "file uploaded"}, status=200)


@token_verification_decorator
@require_http_methods(["PATCH"])
def change_alias(request):
    username = request.username
    try:
        user_info_model = UserInfo.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=401)
    if not request.body:
        return JsonResponse({"error": "Empty request body"}, status=400)
    try:
        data = json.loads(request.body)
        alias = data.get("alias")
        if not alias:
            return JsonResponse({"error": "Alias is required"}, status=400)
        is_valid, message_valid_username = is_valid_username(alias)
        if not is_valid:
            return JsonResponse({'error': message_valid_username }, status=400)
        if alias.endswith("_intra"):
            return JsonResponse({"error": "Alias cannot end with _intra"}, status=400)
        exist = UserInfo.objects.filter(alias=alias).exists()
        if exist:
            return JsonResponse({"error": "Alias already taken."}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    user_info_model.alias = alias
    user_info_model.save(update_fields=["alias"])
    return JsonResponse({"message": "Alias updated successfully"}, status=200)


@token_verification_decorator
@require_http_methods(["POST"])
def send_friend_request(request):
    sender_user = request.username
    try:
        sender_user_model = UserInfo.objects.get(username=sender_user)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    requested_alias = data.get("alias")
    if not requested_alias:
        return JsonResponse({"error": "Alias is required"}, status=400)
    try:
        requested_user_model = UserInfo.objects.get(alias=requested_alias)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)

    if requested_user_model.username == sender_user:
        return JsonResponse({"error": "cannot send a request to yourself"}, status=400)

    if sender_user_model.friends.filter(id=requested_user_model.id).exists():
        return JsonResponse({"error": "Users are already friends"}, status=400)

    if FriendRequest.objects.filter(
        from_user=sender_user_model, to_user=requested_user_model
    ).exists():
        return JsonResponse({"error": "Friend request already sent"}, status=201)

    existing_request = FriendRequest.objects.filter(
        from_user=requested_user_model, to_user=sender_user_model
    )
    if existing_request.exists():
        with transaction.atomic():
            sender_user_model.friends.add(requested_user_model)
            requested_user_model.friends.add(sender_user_model)
            existing_request.delete()
        return JsonResponse({"message": "Friend request accepted and users added as friends"}, status=200)

    FriendRequest.objects.create(
        from_user=sender_user_model, to_user=requested_user_model
    )
    return JsonResponse({"message": "Friend request sent successfully"}, status=200)


@token_verification_decorator
@require_http_methods(["POST"])
def accept_friend_request(request):
    accepter_username = request.username
    try:
        accepter_user_model = UserInfo.objects.get(username=accepter_username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    requester_alias = data.get("alias")
    if not requester_alias:
        return JsonResponse({"error": "Username is required"}, status=400)
    try:
        requester_user_model = UserInfo.objects.get(alias=requester_alias)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        friend_request = FriendRequest.objects.get(
            from_user=requester_user_model, to_user=accepter_user_model
        )
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Friend request does not exist"}, status=404)
    with transaction.atomic():
        accepter_user_model.friends.add(requester_user_model)
        requester_user_model.friends.add(accepter_user_model)
        friend_request.delete()
    return JsonResponse({"message": "Friend request accepted successfully"}, status=200)


@require_http_methods(["POST"])
def decline_friend_request(request):
    decliner_username = request.username
    try:
        decliner_user_model = UserInfo.objects.get(username=decliner_username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    requester_alias = data.get("alias")
    if not requester_alias:
        return JsonResponse({"error": "Alias is required"}, status=400)
    try:
        requester_user_model = UserInfo.objects.get(alias=requester_alias)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        friend_request = FriendRequest.objects.get(
            from_user=requester_user_model, to_user=decliner_user_model
        )
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Friend request does not exist"}, status=404)
    try:
        friend_request.delete()
    except Exception as e:
        return JsonResponse({"error": "Could not delete from data base"}, status=404)
    return JsonResponse({"message": "Friend request declined successfully"}, status=200)


@token_verification_decorator
@require_http_methods(["GET"])
def get_friend_requests(request):
    username = request.username
    try:
        user_model = UserInfo.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    friend_requests = FriendRequest.objects.filter(to_user=user_model).select_related(
        "from_user"
    )
    friend_requests_list = [
        {
            "from_user": friend_request.from_user.alias,
            "timestamp": friend_request.timestamp,
            "photo_profile": friend_request.from_user.photo_profile,
        }
        for friend_request in friend_requests
    ]
    return JsonResponse({"friend_requests": friend_requests_list}, status=200)


@token_verification_decorator
@require_http_methods(["GET"])
def get_friends(request):
    username = request.username
    try:
        user_model = UserInfo.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    friends = user_model.friends.all()
    friends_list = [
        {
            "alias": friend.alias,
            "wins": friend.wins,
            "loses": friend.loses,
            "photo_profile": friend.photo_profile,
            "elo": friend.elo,
            "status": is_user_online(friend.username),
        }
        for friend in friends
    ]
    return JsonResponse({"friends": friends_list}, status=200)


@token_verification_decorator
@require_http_methods(["POST"])
def remove_friend(request):
    username = request.username
    try:
        user_model = UserInfo.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    friend_alias = data.get("alias")
    if not friend_alias:
        return JsonResponse({"error": "Friend alias is required"}, status=400)
    try:
        friend_model = UserInfo.objects.get(alias=friend_alias)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Friend not found"}, status=404)

    if not user_model.friends.filter(id=friend_model.id).exists():
        return JsonResponse({"error": "Users are not friends"}, status=400)
    with transaction.atomic():
        user_model.friends.remove(friend_model)
        friend_model.friends.remove(user_model)
    return JsonResponse({"message": "Friend removed successfully"}, status=200)


@token_verification_decorator
def get_alias_from_token(request):
    username = request.username
    try:
        user_model = UserInfo.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    return JsonResponse({"alias": user_model.alias}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def add_match_history(request):
    try:
        data = json.loads(request.body)
    except Exception as e:
        return
    parsed_data_from_request = parse_add_match_history_request(request)
    if parsed_data_from_request.status_code != 200:
        return parsed_data_from_request
    response_parsed_data = json.loads(parsed_data_from_request.content)
    match_data = response_parsed_data["data"]
    get_oponents_response = get_oponent_usernames_from_match(
        match_data["opponent_1_jwt"], match_data["opponent_2_jwt"]
    )
    if get_oponents_response.status_code != 200:
        return get_oponents_response
    get_oponents_response_json = json.loads(get_oponents_response.content)
    get_oponents_response_data = get_oponents_response_json["data"]
    try:
        opponent_1_model = UserInfo.objects.get(
            username=get_oponents_response_data["opponent_1"]
        )
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        opponent_2_model = UserInfo.objects.get(
            username=get_oponents_response_data["opponent_2"]
        )
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    try:
        elo_calculated = calculate_elo_earned(
            opponent_1_model,
            opponent_2_model,
            match_data["opponent_1_points"],
            match_data["opponent_2_points"],
        )
    except Exception as e:
        return JsonResponse({"error": e}, status=400)
    try:
        MatchHistory.objects.create(
            opponent_1=opponent_1_model,
            opponent_2=opponent_2_model,
            opponent_1_points=match_data["opponent_1_points"],
            opponent_2_points=match_data["opponent_2_points"],
            match_type=match_data["match_type"],
            elo_earned_opponent_1=elo_calculated["opponent_1_earn"],
            elo_earned_opponent_2=elo_calculated["opponent_2_earn"],
            date=datetime.now().strftime("%d-%m-%Y")
        )
    except Exception as e:
        return JsonResponse(
            {"error": e}, status=400
        )
    return update_user_info_after_match(elo_calculated, opponent_1_model, opponent_2_model)


@require_http_methods(["GET"])
def exist_user(request):
    try:
        user_req = request.GET.get("username")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    exist = UserInfo.objects.filter(username=user_req).exists()
    if exist:
        return JsonResponse({"answer": "user exist"}, status=201)
    return JsonResponse({"answer": "user do not exist"}, status=200)


@require_http_methods(["GET"])
def exist_alias(request):
    try:
        alias_req = request.GET.get("alias")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    exist = UserInfo.objects.filter(alias=alias_req).exists()
    if exist:
        return JsonResponse({"answer": "alias exist"}, status=201)
    return JsonResponse({"answer": "alias do not exist"}, status=200)


def get_connected_users(request):
    return JsonResponse({'connected_users': connected_users})

@require_http_methods(["GET"])
def alias_available(request):
    try:
        alias_req = request.GET.get("alias")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    is_valid, message_valid_username = is_valid_username(alias_req)
    if not is_valid:
        return JsonResponse({'error': message_valid_username }, status=400)
    if alias_req.endswith("_intra"):
        return JsonResponse({"error": "Alias cannot end with _intra"}, status=400)
    exist = UserInfo.objects.filter(alias=alias_req).exists()
    if exist:
        logger.warning("ALready exist")
        return JsonResponse({"error": "alias already exist"}, status=400)
    return JsonResponse({"answer": "alias do not exist"}, status=200)


@require_http_methods(["POST"])
@token_verification_decorator
def add_cup_winner(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    password = data.get("password")
    if not password:
        return JsonResponse({"error": "password is required"}, status=400)
    if password != os.environ["SERVICE_PASSWORD"]:
        return JsonResponse({"error": "incorrect password"}, status=400)
    username = request.username
    try:
        user_model = UserInfo.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not registered"}, status=404)
    user_model.cups = user_model.cups + 1
    user_model.save(update_fields=["cups"])
    return JsonResponse({"success": "cup added to user"}, status=200)