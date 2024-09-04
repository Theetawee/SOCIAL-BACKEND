import blurhash
from dj_waanverse_auth.serializers import SignupSerializer as WaanverseSignupSerializer
from PIL import Image
from rest_framework import serializers

from main.utils import upload_profile_image

from .models import Account


class BasicAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "username",
            "name",
            "id",
            "profile_image_url",
            "verified",
            "profile_image_hash",
        ]


class SignupSerializer(WaanverseSignupSerializer):
    name = serializers.CharField(required=False)

    def get_additional_fields(self, validated_data):
        return {"name": validated_data.get("name", "")}


class AccountSerializer(serializers.ModelSerializer):
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "username",
            "email",
            "name",
            "profile_image_url",
            "verified",
            "profile_image_hash",
            "is_self",
            "cover_image_hash",
            "cover_image_url",
            "bio",
            "location",
            "date_joined",
        ]

    def get_is_self(self, obj):
        request = self.context.get("request", None)
        if request and request.user:
            return obj == request.user
        return False


class UpdateProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Account
        fields = ["name", "bio", "location", "profile_image"]

    def update(self, instance, validated_data):
        if "profile_image" in validated_data:
            profile_image = validated_data.pop("profile_image")
            if profile_image:
                try:
                    # Ensure the file is in the correct format
                    profile_image.seek(0)  # Go to the start of the file

                    # Open the image file
                    image = Image.open(profile_image)

                    # Process the image (e.g., creating a thumbnail)
                    image.thumbnail((100, 100))

                    # Generate BlurHash
                    hash = blurhash.encode(image, x_components=4, y_components=3)
                    instance.profile_image_hash = hash

                    # Rewind the file pointer before uploading
                    profile_image.seek(0)

                    # Upload the image to Cloudinary
                    url = upload_profile_image(
                        file=profile_image,
                        username=instance.username,
                        folder="profiles",
                        request=self.context.get("request"),
                    )
                    instance.profile_image_url = url
                except Exception as e:
                    print(f"Error processing image: {e}")

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
