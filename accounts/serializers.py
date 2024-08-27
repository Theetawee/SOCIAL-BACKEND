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
