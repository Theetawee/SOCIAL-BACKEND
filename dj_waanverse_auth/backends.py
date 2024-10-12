
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication as Head

from dj_waanverse_auth.settings import accounts_config

User = get_user_model()


class AuthBackend(BaseBackend):
    """
    Waanverse authentication backend that allows for multiple authentication methods.(username, email, phone_number) refer to docs
    """

    def authenticate(self, request, login_field=None, password=None, **kwargs):
        # Determine which authentication methods are in use
        use_username = "username" in accounts_config.AUTH_METHODS
        use_email = "email" in accounts_config.AUTH_METHODS
        use_phone_number = "phone_number" in accounts_config.AUTH_METHODS
        if not (use_username or use_email or use_phone_number):
            return None

        # Check each method in order of priority
        if use_username and login_field:
            user = self._authenticate_with_username(login_field, password)
            if user is not None:
                return user

        if use_email and login_field:
            user = self._authenticate_with_email(login_field, password)
            if user is not None:
                return user

        if use_phone_number and login_field:
            user = self._authenticate_with_phone_number(login_field, password)
            if user is not None:
                return user

        return None

    def _authenticate_with_username(self, username, password):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def _authenticate_with_email(self, email, password):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def _authenticate_with_phone_number(self, phone_number, password):
        try:
            user = User.objects.get(phone_number__exact=phone_number)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        except Exception:
            # Log the exception or handle it accordingly
            return None


class JWTAuthentication(Head):
    def authenticate(self, request):
        # Try to get the token from the Authorization header
        auth = super().authenticate(request)
        if auth is not None:
            return auth

        # If no token is found in the header, try to get it from cookies
        access_token = request.COOKIES.get(accounts_config.ACCESS_TOKEN_COOKIE)
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                return (user, validated_token)
            except AuthenticationFailed as e:

                raise e

        return None
