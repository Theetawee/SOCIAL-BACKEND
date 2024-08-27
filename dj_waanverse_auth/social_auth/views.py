from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_waanverse_auth.serializers import SignupSerializer

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

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"error": "Authorization code not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                f"Failed to obtain access token: {token_response_data['error_description']}"
            )

        access_token = token_response_data.get("access_token")

        # Get user information
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_params = {"access_token": access_token}
        user_info_response = requests.get(user_info_url, params=user_info_params)
        user_info = user_info_response.json()

        # Implement user authentication or creation
        user = self.authenticate_or_create_user(user_info)

        # Generate JWT or any other token for the authenticated user
        tokens = self.generate_tokens_for_user(user)

        return Response({"tokens": tokens}, status=status.HTTP_200_OK)

    def authenticate_or_create_user(self, user_info, serializer_class):
        email = user_info.get("email")
        username = get_username(user_info)
        random_password = Account.objects.make_random_password()

        if not email:
            raise AuthenticationFailed("No email associated with Google account")

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            # Retrieve serializer fields dynamically

            # Prepare data for user creation
            user_data = {
                "email": email,
                "username": username,
                # Since the passwords are handled by the SignupSerializer, you can set a random one here
                "password1": random_password,
                "password2": random_password,  # Same as password1
            }
            # Instantiate and validate the serializer
            serializer = SignupSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
            else:
                raise AuthenticationFailed(serializer.errors)
        return user

    def generate_tokens_for_user(self, user):
        # Example function to generate JWT tokens for the user
        refresh = "test"
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
