from .models import Account, FriendRequest, Hobby, Friendship
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import AllowAny

from accounts.serializers.create.serializers import (
    UpdateProfileImageSerializer,
    AccountUpdateSerializer,
)

from accounts.serializers.view.serializers import (
    FriendRequestSerializer,
    AccountSerializer,
    HobbySerializer,
)


from dj_rest_auth.app_settings import api_settings

from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from allauth.account.utils import send_email_confirmation
from rest_framework.exceptions import APIException
import blurhash
from PIL import Image
from allauth.account.models import EmailAddress
from dj_rest_auth.views import LoginView
from dj_rest_auth.jwt_auth import set_jwt_cookies
from django.utils import timezone
from rest_framework_simplejwt.settings import (
    api_settings as jwt_settings,
)

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
                serializer.data["profile_image_hash"] = hash_value
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
@permission_classes([AllowAny])
def user_details(request, username):
    try:
        # Retrieve the account associated with the username
        account = get_object_or_404(Account, username=username)
    except Account.DoesNotExist:
        # Return a 404 response if the account does not exist
        return Response(
            {"error": "Account not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.user.is_authenticated:
        # Check if the authenticated user is the same as the requested user
        is_self = request.user.username == username

        # Check friendship status between the authenticated user and the requested account
        account_is_friend = request.user.friends.filter(pk=account.pk).exists()

        # Check friendship status between the requested account and the authenticated user
        user_is_friend = account.friends.filter(pk=request.user.pk).exists()

        # Check if the authenticated user has sent a friend request to the requested account
        user_sent_friend_request = FriendRequest.objects.filter(
            sender=request.user, recipient=account, status="pending"
        ).exists()

        # Check if the requested account has sent a friend request to the authenticated user
        account_sent_friend_request = FriendRequest.objects.filter(
            sender=account, recipient=request.user, status="pending"
        ).exists()

        # Serialize the account data
        serializer = AccountSerializer(account)
        data = serializer.data
        # Add additional data to the serialized account
        data.update(
            {
                "is_self": is_self,
                "account_is_friend": account_is_friend,
                "user_is_friend": user_is_friend,
                "user_sent_friend_request": user_sent_friend_request,
                "account_sent_friend_request": account_sent_friend_request,
            }
        )
        # Return the serialized data as a response
        return Response(data, status=status.HTTP_200_OK)
    else:
        # If the user is not authenticated, return basic details without friendship information
        serializer = AccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def send_friend_request(request, username):
    user = request.user
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if account == user:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if FriendRequest.objects.filter(
        sender=user, recipient=account, status="accepted"
    ).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    friend_request = FriendRequest.objects.create(sender=user, recipient=account)
    friend_request.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_user_friend_requests(request):
    value = request.GET.get("value")
    if value:
        value = int(value)
        friend_requests = FriendRequest.objects.filter(
            recipient=request.user, status="pending"
        )[:value]
    else:
        friend_requests = FriendRequest.objects.filter(
            recipient=request.user, status="pending"
        )
    serializer = FriendRequestSerializer(friend_requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Accept a friend request
@api_view(["POST"])
def accept_friend_request(request, requestId):
    user = request.user
    try:
        friend_request = FriendRequest.objects.get(id=requestId)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    account = friend_request.sender
    friend_request.delete()
    user.friends.add(account)
    user.save()
    return Response(status=status.HTTP_200_OK)


# Decline a friend request


@api_view(["POST"])
def decline_friend_request(request, requestId):
    try:
        friend_request = FriendRequest.objects.get(id=requestId)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    friend_request.status = "declined"
    friend_request.save()
    return Response(status=status.HTTP_200_OK)


class GetHobbies(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = HobbySerializer
    queryset = Hobby.objects.all()
    pagination_class = None


get_hobbies = GetHobbies.as_view()


@api_view(["POST"])
def update_hobbies(request):
    hobbies = request.data.get("hobbies")
    if hobbies:
        try:
            request.user.hobbies.set(hobbies)
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def unfriend_account(request, username):
    try:
        account = Account.objects.get(username=username)
        user = request.user

        # Retrieve the friendship object
        friendship = Friendship.objects.filter(
            (Q(account1=user) & Q(account2=account))
            | (Q(account1=account) & Q(account2=user))
        ).first()

        # If the friendship exists, delete it
        if friendship:
            friendship.delete()
            return Response(
                {"message": "Friendship unfriended successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Friendship does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

    except Account.DoesNotExist:
        return Response(
            {"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND
        )
