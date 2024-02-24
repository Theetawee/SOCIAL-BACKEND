from accounts.models import Account, Badge, FriendRequest, Hobby
from rest_framework import serializers
from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dj_rest_auth.registration.serializers import RegisterSerializer as Cast
from allauth.socialaccount.models import EmailAddress
from allauth.account.utils import setup_user_email
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["name"] = user.name
        token["image"] = user.image
        token["email"] = user.email
        token["image_hash"] = user.profile_image_hash
        token["username"] = user.username
        token["verified"] = user.verified

        return token


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = "__all__"


class RegisterSerializer(Cast):
    name = serializers.CharField(required=True, max_length=255)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if (
                email
                and EmailAddress.objects.is_verified(email)
                or Account.objects.filter(email=email).exists()
            ):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."),
                )
        return email

    def get_cleaned_data(self):
        return {
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "name": self.validated_data.get("name", ""),
            "username": self.validated_data.get("username", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


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


class UpdateProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["profile_image", "profile_image_hash"]


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "phone",
            "gender",
            "date_of_birth",
            "bio",
            "name",
            "location",
            "hobbies",
        ]


# Serializer to add or update User Email


class EmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=Account.objects.all(),
                message="Email already exists.",
            )
        ],
    )

    class Meta:
        model = Account
        fields = ["email"]


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = AccountSerializer()
    recipient = AccountSerializer()

    class Meta:
        model = FriendRequest
        fields = "__all__"


class UpdateHobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["hobbies"]

    def update(self, instance, validated_data):
        instance.hobbies.set(validated_data.get("hobbies", instance.hobbies))
        instance.save()
        return instance
