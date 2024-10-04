from dj_waanverse_auth.serializers import SignupSerializer as WaanverseSignupSerializer
from rest_framework import serializers

from main.utils import get_image_hash, upload_profile_image

from .models import Account


class BasicAccountSerializer(serializers.ModelSerializer):
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "username",
            "name",
            "id",
            "profile_image_url",
            "verified",
            "profile_image_hash",
            "is_self",
            "verified_company",
        ]

    def get_is_self(self, obj):
        request = self.context.get("request", None)
        if request and request.user:
            return obj == request.user
        return False


class AccountSerializer(BasicAccountSerializer):
    class Meta(BasicAccountSerializer.Meta):
        model = Account
        fields = BasicAccountSerializer.Meta.fields + [
            "email",
            "cover_image_hash",
            "cover_image_url",
            "bio",
            "location",
            "date_joined",
        ]


class SignupSerializer(WaanverseSignupSerializer):
    name = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)

    def get_additional_fields(self, validated_data):
        return {
            "name": validated_data.get("name", ""),
            "gender": validated_data.get("gender", None),
        }


class UpdateProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(write_only=True, required=False)
    cover_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Account
        fields = ["name", "bio", "location", "profile_image", "cover_image"]

    def update(self, instance, validated_data):
        if "profile_image" in validated_data:
            profile_image = validated_data.pop("profile_image")
            if profile_image:
                try:
                    hash = get_image_hash(profile_image)
                    instance.profile_image_hash = hash

                    # Rewind the file pointer before uploading
                    profile_image.seek(0)

                    # Upload the image to Cloudinary
                    url = upload_profile_image(
                        file=profile_image,
                        file_name=instance.username,
                        folder="profiles",
                        request=self.context.get("request"),
                    )
                    instance.profile_image_url = url
                except Exception as e:
                    print(f"Error processing image: {e}")
        if "cover_image" in validated_data:
            cover_image = validated_data.pop("cover_image")
            if cover_image:
                try:
                    hash = get_image_hash(cover_image)
                    instance.cover_image_hash = hash

                    # Rewind the file pointer before uploading
                    cover_image.seek(0)

                    # Upload the image to Cloudinary
                    url = upload_profile_image(
                        file=cover_image,
                        file_name=f"cover_{instance.username}",
                        folder="covers",
                        request=self.context.get("request"),
                    )
                    instance.cover_image_url = url
                except Exception as e:
                    print(f"Error processing image: {e}")
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
