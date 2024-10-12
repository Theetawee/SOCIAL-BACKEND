import string
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_waanverse_auth.messages import Messages
from dj_waanverse_auth.settings import accounts_config
from dj_waanverse_auth.signals import user_created_via_google
from dj_waanverse_auth.utils import (
    check_mfa_status,
    generate_tokens,
    get_email_verification_status,
    get_serializer,
    handle_email_verification,
    handle_user_login,
    set_cookies,
)

from .utils import get_username

Account = get_user_model()


@api_view(["GET"])
@permission_classes([AllowAny])
def google_url(request):
    try:
        google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        url = f"{google_auth_url}?{urlencode(params)}"
    except AttributeError:
        return Response(
            {"error": "Google OAuth settings are not properly configured"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"url": url}, status=status.HTTP_200_OK)


class GoogleAuthCallbackView(APIView):
    permission_classes = (AllowAny,)
    is_created = False

    def post(self, request):
        code = request.data.get("code")
        credential = request.data.get("credential")
        print("here calling")
        if credential:
            print("here")
            # Handle Google One Tap login
            try:
                user_info = self.verify_google_credential(credential)
            except AuthenticationFailed as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif code:
            # Handle Google OAuth2 code flow
            user_info = self.exchange_code_for_user_info(code)
        else:
            return Response(
                {"error": "Authorization code or credential not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Implement user authentication or creation
        user = self.authenticate_or_create_user(user_info)
        mfa_status = check_mfa_status(user)
        email_verification_status = get_email_verification_status(user)
        USER_CLAIM_SERIALIZER = get_serializer(
            accounts_config.USER_CLAIM_SERIALIZER_CLASS
        )
        if not email_verification_status:
            if accounts_config.AUTO_RESEND_EMAIL and self.is_created is False:
                handle_email_verification(user)

            response_data = {
                "email": user.email,
                "msg": Messages.status_unverified,
                "code": "email_unverified",
            }
            return Response(response_data, status=status.HTTP_200_OK)

        if mfa_status:
            pass  # MFA handling can be added here
        else:
            tokens = generate_tokens(user)
            response = Response(
                data={
                    "access_token": tokens.get("access_token"),
                    "refresh_token": tokens.get("refresh_token"),
                    "user": USER_CLAIM_SERIALIZER(user).data,
                },
                status=status.HTTP_200_OK,
            )
            handle_user_login(user=user, context={"request": request})
            new_response = set_cookies(
                response=response,
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token"),
            )

        return new_response

    def exchange_code_for_user_info(self, code):
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=token_data)
        token_response_data = token_response.json()

        if "error" in token_response_data:
            raise AuthenticationFailed(
                f"Failed to obtain access token: {token_response_data.get('error_description', 'Unknown error')}"
            )

        access_token = token_response_data.get("access_token")

        # Get user information
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_params = {"access_token": access_token}
        user_info_response = requests.get(user_info_url, params=user_info_params)
        user_info = user_info_response.json()

        if "error" in user_info:
            raise AuthenticationFailed("Failed to fetch user info from Google")

        return user_info

    def verify_google_credential(self, credential):
        # Verify the Google ID token (One Tap credential) by sending it to Google's endpoint
        verify_url = "https://oauth2.googleapis.com/tokeninfo"
        response = requests.get(verify_url, params={"id_token": credential})
        response_data = response.json()

        if "error" in response_data:
            raise AuthenticationFailed(
                f"Invalid credential: {response_data.get('error_description', 'Unknown error')}"
            )

        # You can also check if the token audience matches your client ID
        if response_data.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("Token audience mismatch")

        return {
            "email": response_data.get("email"),
            "verified_email": response_data.get("email_verified"),
            "name": response_data.get("name"),
            "picture": response_data.get("picture"),
        }

    def authenticate_or_create_user(self, user_info):
        email = user_info.get("email")
        username = get_username(user_info)
        email_verified = user_info.get("verified_email", False)
        allowed_chars = string.ascii_letters + string.digits + string.punctuation
        password = get_random_string(
            length=16,
            allowed_chars=allowed_chars,
        )
        CREATION_SERIALIZER = get_serializer(
            accounts_config.REGISTRATION_SERIALIZER_CLASS
        )

        if not email:
            raise AuthenticationFailed("No email associated with Google account")

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            self.is_created = True
            # Prepare data for user creation
            user_data = {
                "email": email,
                "username": username,
                "password1": password,
                "password2": password,
                "verified": email_verified,
            }
            # Instantiate and validate the serializer
            serializer = CREATION_SERIALIZER(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                user_created_via_google.send(
                    sender=self.__class__, user=user, user_info=user_info
                )
            else:
                raise AuthenticationFailed(serializer.errors)

        return user
