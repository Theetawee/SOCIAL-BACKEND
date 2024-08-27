from urllib.parse import urlencode

import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account

from .serializers import BasicAccountSerializer


class UserList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BasicAccountSerializer
    pagination_class = None

    def get_queryset(self):
        username = self.request.query_params.get("username", None)

        if username:
            return Account.objects.filter(username__icontains=username)[:5]
        return Account.objects.none()


user_list = UserList.as_view()


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

    def authenticate_or_create_user(self, user_info):
        # Example function to authenticate or create a user
        email = user_info.get("email")
        if not email:
            raise AuthenticationFailed("No email associated with Google account")

        print(user_info)

        return "test"

    def generate_tokens_for_user(self, user):
        # Example function to generate JWT tokens for the user
        refresh = "test"
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
