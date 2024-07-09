from .models import Account
from rest_framework import serializers

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
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


class BasicAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "username",
            "name",
            "verified",
        ]


class AccountSerializer(BasicAccountSerializer):
    class Meta(BasicAccountSerializer.Meta):
        model = Account
        fields = BasicAccountSerializer.Meta.fields + [
            "email",
            "date_joined",
            "last_login",
        ]
