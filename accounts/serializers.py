from rest_framework import serializers
from .models import Account


class BasicAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["username", "name", "id", "image", "verified", "profile_image_hash"]
