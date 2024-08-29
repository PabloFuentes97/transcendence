from django.urls import path

from . import views

urlpatterns = [
    path("get_user_info", views.get_user_info, name="get_user_info"),
    path("create_user_info", views.create_user_info, name="create_user_info"),
    path("upload_profile_photo", views.upload_profile_photo, name="upload_profile_photo"),
    path("change_alias", views.change_alias, name="change_alias"),
    path("exist_user", views.exist_user, name="exist_user"),
    path("exist_alias", views.exist_alias, name="exist_alias"),
    path("get_my_user_info", views.get_my_user_info, name="get_my_user_info"),
    path("send_friend_request", views.send_friend_request, name="send_friend_request"),
    path("accept_friend_request", views.accept_friend_request, name="accept_friend_request"),
    path("decline_friend_request", views.decline_friend_request, name="decline_friend_request"),
    path("get_friend_requests", views.get_friend_requests, name="get_friend_requests"),
    path("get_friends", views.get_friends, name="get_friends"),
    path("remove_friend", views.remove_friend, name="remove_friend"),
    path("add_match_history", views.add_match_history, name="add_match_history"),
    path("get_all_users_info", views.get_all_users_info, name="get_all_users_info"),
    path("get_connected_users", views.get_connected_users, name="get_connected_users"),
    path("get_user_info_from_alias", views.get_user_info_from_alias, name="get_user_info_from_alias"),
    path("alias_available", views.alias_available, name="alias_available"),
    path("get_alias_from_token", views.get_alias_from_token, name="get_alias_from_token"),
    path("add_cup_winner", views.add_cup_winner, name="add_cup_winner")
]