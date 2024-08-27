from django.urls import include, path

from .social_auth import urls as social_auth_urls
from .views import (
    DeactivateMfaView,
    enable_mfa,
    index,
    login_view,
    logout_view,
    mfa_login,
    mfa_status,
    refresh_token_view,
    regenerate_recovery_codes,
    resend_verification_email,
    reset_password,
    signup_view,
    user_info,
    verify_email,
    verify_mfa,
    verify_reset_password,
)

urlpatterns = [
    path("login", login_view, name="login"),
    path("token/refresh", refresh_token_view, name="refresh_token"),
    path("resend/email", resend_verification_email, name="resend_verification_email"),
    path("verify/email", verify_email, name="verify_email"),
    path("signup", signup_view, name="signup"),
    path("me", user_info, name="user_info"),
    path("mfa/activate", enable_mfa, name="activate_mfa"),
    path("mfa/verify", verify_mfa, name="verify_mfa"),
    path("mfa/status", mfa_status, name="mfa_status"),
    path("mfa/regenerate-codes", regenerate_recovery_codes, name="regenerate_codes"),
    path("mfa/deactivate", DeactivateMfaView.as_view(), name="deactivate_mfa"),
    path("logout", logout_view, name="logout"),
    path("mfa/login", mfa_login, name="mfa_login"),
    path("password/reset", reset_password, name="reset_password"),
    path("password/reset/new", verify_reset_password, name="verify_reset_password"),
    path("", index, name="index"),
    path("google/", include(social_auth_urls)),
]
