from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(serializers.Serializer):
    login_field = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        login_field = data.get("login_field")
        password = data.get("password")

        if not login_field or not password:
            raise serializers.ValidationError(
                _("Please provide both login field and password.")
            )

        # Authenticate the user using the custom backend
        user = authenticate(
            request=self.context.get("request"),
            login_field=login_field,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError({"msg": _("Invalid login credentials.")})

        if not user.is_active:
            raise serializers.ValidationError({"msg": _("This account is inactive.")})

        # Generate the token using TokenObtainPairSerializer
        refresh = TokenObtainPairSerializer.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
            },
        }
