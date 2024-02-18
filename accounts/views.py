from .models import Account,FriendRequest
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.response import Response
from .serializers import (
    AccountSerializer,
    AccountSerializer,
    UpdateProfileImageSerializer,
    AccountUpdateSerializer
)
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


@api_view(["GET"])
def user_details(request, username):
    try:
        # Check if the requested username is the same as the authenticated user
        is_self = request.user.username == username

        # Get the account associated with the username
        account = Account.objects.get(username=username)

        # Check if the authenticated user is friends with the requested account
        account_is_friend = account in request.user.friends.all()

        # Check if the requested account is friends with the authenticated user
        user_is_friend = request.user in account.friends.all()

        # Check if the authenticated user has sent a friend request to the requested account
        user_sent_friend_request = FriendRequest.objects.filter(sender=request.user, recipient=account, status='pending').exists()

        # Check if the requested account has sent a friend request to the authenticated user
        account_sent_friend_request = FriendRequest.objects.filter(sender=account, recipient=request.user, status='pending').exists()

        # Serialize the account data
        serializer = AccountSerializer(account)
        data=serializer.data
        # Add additional data to the serialized account
        data['is_self'] = is_self
        data['account_is_friend'] = account_is_friend
        data['user_is_friend'] = user_is_friend
        data['user_sent_friend_request'] = user_sent_friend_request
        data['account_sent_friend_request'] = account_sent_friend_request
        # Return the serialized data as a response
        return Response(data, status=status.HTTP_200_OK)

    except Account.DoesNotExist:
        # Return a 404 response if the account does not exist
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def send_friend_request(request,username):
    user = request.user
    try:
        account=Account.objects.get(username=username)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if(account == user):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if(FriendRequest.objects.filter(sender=user,recipient=account).exists()):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    friend_request = FriendRequest.objects.create(sender=user,recipient=account)
    friend_request.save()
    return Response(status=status.HTTP_200_OK)
