import blurhash
from PIL import Image
from rest_framework import serializers

from dj_waanverse_auth.serializers import SignupSerializer as WaanverseSignupSerializer

from .models import Account


class BasicAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["username", "name", "id", "image", "verified", "profile_image_hash"]


class SignupSerializer(WaanverseSignupSerializer):
    name = serializers.CharField(required=True)

    def get_additional_fields(self, validated_data):
        return {"name": validated_data["name"]}


class AccountSerializer(serializers.ModelSerializer):
    is_self = serializers.SerializerMethodField()
    header = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "username",
            "email",
            "name",
            "image",
            "verified",
            "profile_image_hash",
            "is_self",
            "header",
            "cover_image_hash",
            "bio",
            "location",
            "date_joined",
        ]

    def get_is_self(self, obj):
        request = self.context.get("request", None)
        if request and request.user:
            return obj == request.user
        return False

    def get_header(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        else:
            return None


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["name", "bio", "location", "profile_image"]

    def update(self, instance, validated_data):
        if validated_data.get("profile_image"):
            try:
                with Image.open(validated_data["profile_image"]) as image:
                    image.thumbnail((100, 100))
                    hash = blurhash.encode(image, x_components=4, y_components=3)
                    instance.profile_image_hash = hash
            except Exception:
                pass
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
