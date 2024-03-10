from rest_framework import serializers
from accounts.models import Badge, Account, Hobby, FriendRequest


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            "id",
            "name",
            "image",
            "description",
            "value",
            "image_hash",
            "added_on",
            "updated_on",
        ]


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    badges = BadgeSerializer(many=True)
    hobbies = HobbySerializer(many=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "gender",
            "date_of_birth",
            "image",
            "bio",
            "verified",
            "name",
            "profile_image_hash",
            "location",
            "badges",
            "joined",
            "hobbies",
        ]


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = AccountSerializer()
    recipient = AccountSerializer()

    class Meta:
        model = FriendRequest
        fields = "__all__"


class SuggestedAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["username", "id", "profile_image_hash", "verified", "image", "name"]
