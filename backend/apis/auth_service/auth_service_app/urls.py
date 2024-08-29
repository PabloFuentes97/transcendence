from django.urls import path

from . import views

urlpatterns = [
    path('verify_token/', views.verify_token, name='verify_token'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('login_intra/', views.login_intra, name='login_intra'),
    path('start_auth_intra/', views.start_auth_intra, name='start_auth_intra'),
    path('enable_2fa/', views.enable_2fa, name='enable_2fa'),
    path('is_2fa_enabled/', views.is_2fa_enabled, name='is_2fa_enabled'),
    path('disable_2fa/', views.disable_2fa, name='disable_2fa'),
    path('change_password/', views.change_password, name='change_password'),
    path('is_from_intra/', views.is_from_intra, name='is_from_intra')
]
