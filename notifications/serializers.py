from rest_framework.serializers import ModelSerializer
from .models import SubscriptionInfo, PushInformation,Notification
from accounts.serializers import AccountSerializer
from posts.serializers import PostSerializer, CommentSerializer

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionInfo
        fields = ("endpoint", "auth", "p256dh", "user_agent")


class WebPushSerializer(ModelSerializer):
    class Meta:
        model = PushInformation
        fields = "__all__"

    def save(self, subscription, user):
        data = {"user": user, "subscription": subscription}

        push_info, created = PushInformation.objects.get_or_create(**data)
        return push_info


class NotificationSerializer(ModelSerializer):
    post=PostSerializer()
    comment=CommentSerializer()
    to_user=AccountSerializer()
    from_user=AccountSerializer()
    class Meta:
        model = Notification
        fields = ['post','comment','to_user','from_user','timestamp','type','is_read','id']
