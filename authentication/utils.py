from django.conf import settings
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_cookie_settings():
    """
    Returns common settings for setting cookies based on the environment (debug/production).
    """
    SECURE_COOKIES = not settings.DEBUG
    COOKIE_PATH = "/"
    COOKIES_DOMAIN = "alloqet.com" if not settings.DEBUG else None
    SAMESITE = "Lax"

    return {
        "secure": SECURE_COOKIES,
        "domain": COOKIES_DOMAIN,
        "path": COOKIE_PATH,
        "samesite": SAMESITE,
    }


def set_cookie(response, token, token_type):
    """
    Helper function to set cookies for access and refresh tokens.
    """
    cookie_settings = get_cookie_settings()

    if token_type == "access":
        ACCESS_LIFETIME = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        response.set_cookie(
            "access",
            token,
            max_age=ACCESS_LIFETIME,
            httponly=True,
            secure=cookie_settings["secure"],
            domain=cookie_settings["domain"],
            path=cookie_settings["path"],
            samesite=cookie_settings["samesite"],
        )
    elif token_type == "refresh":
        REFRESH_LIFETIME = api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()
        response.set_cookie(
            "refresh",
            token,
            max_age=REFRESH_LIFETIME,
            httponly=True,
            secure=cookie_settings["secure"],
            domain=cookie_settings["domain"],
            path=cookie_settings["path"],
            samesite=cookie_settings["samesite"],
        )


def handle_login_tokens(user):
    """
    Generate access and refresh tokens for the user upon login.
    """
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token

    return {"refresh": str(refresh_token), "access": str(access_token)}
