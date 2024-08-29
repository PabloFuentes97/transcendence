from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .models import UserAuth
from .tools import get_token_from_intra, get_info_from_intra_token, register_user_from_intra, create_user_api_call, delete_user_auth, is_valid_username, is_2fa_code_valid, alias_exist_user_info, error_2fa_code, MAX_LENGHT_PASSWORD, MAX_LENGHT_USERNAME
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from django.http import JsonResponse, HttpResponseRedirect
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
import os
import requests
import json
import logging
import pyotp
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not username or not password:
        return JsonResponse({'error': 'Username and password are required.'}, status=400)
    if len(password) > MAX_LENGHT_PASSWORD:
            return JsonResponse({'error': 'Username or password too long'}, status=400)
    is_valid, message_valid_username = is_valid_username(username)
    if not is_valid:
        return JsonResponse({'error': message_valid_username }, status=400)
    exist = UserAuth.objects.filter(username=username).exists()
    if exist:
        return JsonResponse({'error': 'Username already taken.'}, status=400)
    if alias_exist_user_info(username):
        return JsonResponse({'error': 'Username already taken.'}, status=400)
    hash_password = generate_password_hash(
        password=password,
        method="pbkdf2:sha256",
        salt_length=8)
    key_2fa = pyotp.random_base32()
    new_user = UserAuth(
        username=username,
        password=hash_password,
        key_2fa=key_2fa
    )
    new_user.save()
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    jwt_token = jwt.encode(payload, os.environ.get("SECRET_JWT"), algorithm='HS256')
    response_create_user = create_user_api_call(username, "/images/default_profile_photo.jpg", username, jwt_token)
    if response_create_user.status_code != 200:
        delete_user_auth(username)
        return response_create_user
    return JsonResponse({'token': jwt_token}, status=200)


@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        otp_code = data.get('otp')
        if len(username) > MAX_LENGHT_USERNAME or len(password) > MAX_LENGHT_PASSWORD:
            return JsonResponse({'error': 'Username or password too long'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not username or not password:
        return JsonResponse({'error': 'Username and password are required.'}, status=400)
    try:
        user_selected = UserAuth.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=401)
    if not check_password_hash(user_selected.password, password):
        return JsonResponse({'error': 'Incorrect password'}, status=401)

    if user_selected.is_2fa_enabled:
        if not otp_code:
            return JsonResponse({'requires2FA': True}, status=200)
        if not is_2fa_code_valid(otp_code, user_selected):
            return JsonResponse({'error': 'Invalid OTP'}, status=401)

    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    jwt_token = jwt.encode(payload, os.environ.get("SECRET_JWT"), algorithm='HS256')
    return JsonResponse({'token': jwt_token}, status=200)


def verify_token(request):
    token = request.headers.get('Authorization')
    if not token:
        return JsonResponse({'error': 'Token is required'}, status=400)
    try:
        if 'Bearer ' in token:
            token = token.replace('Bearer ', '')
        decoded = jwt.decode(token, os.environ.get("SECRET_JWT"), algorithms=['HS256'])
        return JsonResponse({'username': decoded['username']}, status=200)
    except ExpiredSignatureError:
        return JsonResponse({'error': 'Token has expired'}, status=401)
    except InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def start_auth_intra(request):
    client_id = os.environ.get("INTRA_UID")
    localhost = os.environ.get("LOCALHOST")
    redirect_uri = f"https://{localhost}:4043/auth_service/login_intra/"
    auth_url = f"https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=public"
    return HttpResponseRedirect(auth_url)

@csrf_exempt
def login_intra(request):
    try:
        response_from_get_token_from_intra = get_token_from_intra(request)
        if response_from_get_token_from_intra.status_code != 200:
            return HttpResponse("error getting token from the intra")
        access_token_from_intra = response_from_get_token_from_intra.json()["access_token"]
        response_intra_login_info = get_info_from_intra_token(access_token_from_intra)
        if response_intra_login_info["status_code"] != 200:
            return HttpResponse(response_intra_login_info["error"])
        response_from_register_from_intra = register_user_from_intra(response_intra_login_info["response_info"])
        if response_from_register_from_intra["status_code"] != 200:
                return HttpResponse(response_from_register_from_intra["error"])
        jwt_token = response_from_register_from_intra["token"]
        return HttpResponse(f"""
            <html>
            <body>
                <script>
                    window.localStorage.setItem('jwtToken', "{jwt_token}");
                    window.close();
                </script>
            </body>
            </html>
        """)
    except Exception as e:
        return HttpResponse(e)
        
@csrf_exempt
@require_http_methods(["POST"])
def enable_2fa(request):
    response_verification_toke = verify_token(request)
    if response_verification_toke.status_code != 200:
        return response_verification_toke
    try:
        data = json.loads(request.body)
        code = data.get('code_2fa')
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not code:
        return JsonResponse({'error': 'OTP code required.'}, status=400)
    if not error_2fa_code(code):
        return JsonResponse({'error': 'Invald OTP'}, status=400)
    try:
        data_response = json.loads(response_verification_toke.content)
        username = data_response["username"]
        user_selected = UserAuth.objects.get(username=username)
        if user_selected.is_2fa_enabled:
            return JsonResponse({'error': 'OTP already enabled'}, status=400)
        if user_selected.is_from_intra:
            return JsonResponse({'error': 'not OTP from login intra'}, status=401)
        if not is_2fa_code_valid(code, user_selected):
            return JsonResponse({'error': 'Invalid OTP'}, status=401)
        user_selected.is_2fa_enabled = True
        user_selected.save()
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=401)
    return JsonResponse({'message': "enabled 2fa"}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def is_2fa_enabled(request):
    response_verification_token = verify_token(request)
    if response_verification_token.status_code != 200:
        return response_verification_token
    try:
        data_response = json.loads(response_verification_token.content)
        username = data_response["username"]
        user_selected = UserAuth.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=401)
    if user_selected.is_2fa_enabled:
        return JsonResponse({'is_2fa_enabled': user_selected.is_2fa_enabled}, status=200)
    uri = pyotp.totp.TOTP(user_selected.key_2fa).provisioning_uri(name=username,
                                                issuer_name="transcendence")
    return JsonResponse({'answer': False, 'uri': uri}, status=200)

    
@csrf_exempt
@require_http_methods(["POST"])
def disable_2fa(request):
    response_verification_toke = verify_token(request)
    if response_verification_toke.status_code != 200:
        return response_verification_toke
    try:
        data = json.loads(request.body.decode('utf-8')) 
        otp_code = data.get('code_2fa')
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not otp_code:
        return JsonResponse({'error': 'otp code is required.'}, status=400)
    if not error_2fa_code(otp_code):
        return JsonResponse({'error': 'Invald OTP'}, status=400)
    try:
        data_response = json.loads(response_verification_toke.content)
        username = data_response["username"]
        user_selected = UserAuth.objects.get(username=username)
        if not user_selected.is_2fa_enabled:
            return JsonResponse({'error': '2FA already disabled'}, status=400)
        if not is_2fa_code_valid(otp_code, user_selected):
            return JsonResponse({'error': 'Invalid OTP'}, status=401)
        user_selected.is_2fa_enabled = False
        user_selected.save()
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=401)
    return JsonResponse({'message': '2FA disabled'}, status=200)


@require_http_methods(["POST"])
def change_password(request):
    response_verification_toke = verify_token(request)
    if response_verification_toke.status_code != 200:
        return response_verification_toke
    try:
        data_response = json.loads(response_verification_toke.content)
        username = data_response["username"]
        user_selected = UserAuth.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=401)
    if user_selected.is_from_intra:
        return JsonResponse({'error': 'not password change from login intra'}, status=401)
    try:
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not check_password_hash(user_selected.password, old_password):
        return JsonResponse({'error': 'Incorrect password'}, status=401)
    if len(new_password) > 40:
        return JsonResponse({'error': 'Password too long'}, status=400)
    hash_password = generate_password_hash(
        password=new_password,
        method="pbkdf2:sha256",
        salt_length=8)
    user_selected.password = hash_password
    user_selected.save(update_fields=["password"])
    return JsonResponse({'success': "Password changed"}, status=200)


@require_http_methods(["GET"])
def is_from_intra(request):
    response_verification_toke = verify_token(request)
    if response_verification_toke.status_code != 200:
        return response_verification_toke
    try:
        data_response = json.loads(response_verification_toke.content)
        username = data_response["username"]
        user_selected = UserAuth.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not registered'}, status=401)
    return JsonResponse({'from_intra': user_selected.is_from_intra }, status=200)
    


        


