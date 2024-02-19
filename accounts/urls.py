from django.urls import path, include
from .views import (
    loggedInUser,resend_email,update_profile_image,update_profile_info,user_details,send_friend_request,get_user_friend_requests
)
from dj_rest_auth.registration.views import VerifyEmailView
from accounts.authentication import GoogleLogin

from dj_rest_auth.views import (
    PasswordResetConfirmView,
)


"""
Accounts Endpoints
- login = /accounts/login/
- register = /accounts/signup/
"""


urlpatterns = [
    path("me/", loggedInUser),
    path(
        "activate/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("signup/", include("dj_rest_auth.registration.urls")),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("resend_email/", resend_email),
    path('update/image/',update_profile_image),
    path('update/info/',update_profile_info),
    path('user/<str:username>/',user_details),
    path('send-friend-request/<str:username>/',send_friend_request),
    path('friend-requests/',get_user_friend_requests)
]


