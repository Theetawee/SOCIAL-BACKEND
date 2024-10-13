from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account

from .serializers import (AccountSerializer, BasicAccountSerializer,
                          UpdateProfileSerializer)


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


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    lookup_field = "username"

    def get_serializer_context(self):
        """Add additional context to the serializer."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


user_detail = UserDetail.as_view()


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    try:
        account = Account.objects.get(username=user.username)
    except Account.DoesNotExist:
        return Response(
            {"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = UpdateProfileSerializer(
        account, data=request.data, partial=True, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def basic_user_info(request, username):
    try:
        user = Account.objects.get(username=username)
        serializer = BasicAccountSerializer(user, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def user_account_action(request, action, username):
    """Handle follow or unfollow action."""
    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED
        )

    user_to_follow = get_object_or_404(Account, username=username)

    if action not in ["follow", "unfollow"]:
        return Response(
            {"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if action == "follow":
            request.user.follow(user_to_follow)
        elif action == "unfollow":
            request.user.unfollow(user_to_follow)

        return Response(data={"action": action}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
