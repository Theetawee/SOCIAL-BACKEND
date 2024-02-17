from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SubscriptionSerializer, WebPushSerializer,NotificationSerializer
from .utils import send_user_notification
from rest_framework import generics
from .models import Notification
from django.db.models import Q
import time


@api_view(["POST"])
def save_info(request):
    try:
        post_data = request.data
        user = request.user
    except ValueError:
        return Response(
            {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
        )

    subscription_data = post_data.get("subscription", {})
    subscription_data["user_agent"] = post_data.get("user_agent", "")
    # Extract auth and p256dh from the nested keys
    keys = subscription_data.get("keys", {})
    subscription_data["auth"] = keys.get("auth", "")
    subscription_data["p256dh"] = keys.get("p256dh", "")
    try:
        subscription_serializer = SubscriptionSerializer(data=subscription_data)
        subscription_serializer.is_valid(raise_exception=True)

        # Save the subscription
        subscription = subscription_serializer.save()
        # Create a dictionary with user and subscription_pk

        web_push_data = {
            "subscription": subscription.pk,
            "user": user.pk,
        }
        web_push_serializer = WebPushSerializer(data=web_push_data)
        web_push_serializer.is_valid(raise_exception=True)

        # Save the web push information
        web_push_serializer.save(subscription, user)
    except:
        print('exists')
        pass
    payload = {
        "head": "Waanverse",
        "body": "Welcome to Waanverse",
        "icon": "https://theetawee.github.io/social_app_files/images/logo.svg",
        "url": "/",
        "badge": "https://theetawee.github.io/social_app_files/images/badge.png",
    }
    send_user_notification(user, payload,ttl=1000)

    return Response(post_data, status=status.HTTP_201_CREATED)



class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        user_notifications=Notification.objects.filter(Q(to_user=user)|Q(is_read=False))
        return user_notifications

notifications=NotificationList.as_view()



@api_view(["GET"])
def notifications_seen(request,pk):
    notification=Notification.objects.get(pk=pk)
    notification.is_read=True
    notification.save()

    return Response({"message": "success"}, status=status.HTTP_200_OK)
