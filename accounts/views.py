from .models import Account
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
    AccountSerializer,
    AccountSerializer,
    UpdateProfileImageSerializer,
    AccountUpdateSerializer
)
from dj_rest_auth.jwt_auth import set_jwt_cookies
from django.utils import timezone
from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.views import LoginView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import get_object_or_404
from allauth.account.admin import EmailAddress
from allauth.account.utils import send_email_confirmation
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
import blurhash
from PIL import Image
from allauth.account.models import EmailAddress
from rest_framework_simplejwt.settings import (
    api_settings as jwt_settings,
)
from .utils import generate_secure_key
from rest_framework_simplejwt.views import TokenObtainPairView





# Create your views here.


class NewEmailConfirmation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = get_object_or_404(Account, email=request.data["email"])

            emailAddress = EmailAddress.objects.filter(
                user=user, verified=True
            ).exists()
        except Exception as e:
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













@api_view(["GET"])
def loggedInUser(request):
    user = request.user
    serializer = AccountSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_profile_image(request):
    serializer = UpdateProfileImageSerializer(
        instance=request.user, data=request.data, partial=True
    )

    if serializer.is_valid():
        updated_user = serializer.save()

        if "profile_image" in serializer.validated_data:
            # Check if the 'profile_image' field is present in the data
            image_file = updated_user.profile_image
            with Image.open(image_file) as image:
                image.thumbnail((100, 100))
                hash_value = blurhash.encode(image, x_components=4, y_components=3)
                updated_user.profile_image_hash = hash_value
                updated_user.save()
                print(hash_value)
                serializer.data["profile_image_hash"] = hash_value
                print("yea")
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def update_profile_info(request):
    serializer = AccountUpdateSerializer(
        instance=request.user, data=request.data, partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
