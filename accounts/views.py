from .models import Account
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from dj_rest_auth.app_settings import api_settings

from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from allauth.account.utils import send_email_confirmation
from rest_framework.exceptions import APIException
from allauth.account.models import EmailAddress
from dj_rest_auth.views import LoginView
from dj_rest_auth.jwt_auth import set_jwt_cookies
from django.utils import timezone
from rest_framework_simplejwt.settings import (
    api_settings as jwt_settings,
)
from .serializers import AccountSerializer

# Create your views here.


class NewEmailConfirmation(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = get_object_or_404(Account, email=request.data["email"])

            emailAddress = EmailAddress.objects.filter(
                user=user, verified=True
            ).exists()
        except Exception:
            return Response(
                {"message": "This email does not exist"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if emailAddress:
            return Response(
                {"message": "This email is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            try:
                send_email_confirmation(request, user=user)
                return Response(
                    {"message": "Email confirmation sent"},
                    status=status.HTTP_201_CREATED,
                )
            except APIException:
                return Response(
                    {
                        "message": "This email does not exist, please create a new account"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )


resend_email = NewEmailConfirmation.as_view()


class CustomLoginView(LoginView):

    def get_response(self):
        serializer_class = self.get_response_serializer()

        # set_device(self.user,self.request)

        access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
        refresh_token_expiration = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME
        return_expiration_times = api_settings.JWT_AUTH_RETURN_EXPIRATION

        data = {
            "user": self.user,
            "access": self.access_token,
        }
        data["refresh"] = self.refresh_token

        if return_expiration_times:
            data["access_expiration"] = access_token_expiration
            data["refresh_expiration"] = refresh_token_expiration

        serializer = serializer_class(
            instance=data,
            context=self.get_serializer_context(),
        )

        response = Response(serializer.data, status=status.HTTP_200_OK)

        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response


@api_view(["GET"])
def loggedInUser(request):
    user = request.user
    serializer = AccountSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
