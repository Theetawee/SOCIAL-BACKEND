import pyotp
from django.contrib.auth import get_user_model, logout, user_logged_in
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .messages import Messages
from .models import MultiFactorAuth
from .serializers import (
    DeactivateMfaSerializer,
    LoginSerializer,
    LogoutSerializer,
    MfaCodeSerializer,
    ResendVerificationEmailSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
    VerifyResetPasswordSerializer,
)
from .settings import accounts_config
from .utils import (
    generate_tokens,
    get_client_ip,
    get_serializer,
    get_user_agent,
    handle_email_mechanism,
    reset_response,
    set_cookies,
)

Account = get_user_model()


@api_view(["GET"])
@permission_classes([AllowAny])
def index(request):
    data = "Welcome to Dj Waanverse Auth. Docs \n Docs - https://dj-waanverse-auth.waanverse.com "
    return Response(status=status.HTTP_200_OK, data=data)


@api_view(["POST"])
@throttle_classes([UserRateThrottle])
@permission_classes([AllowAny])
def login_view(request):
    USER_CLAIM_SERIALIZER = get_serializer(accounts_config.USER_CLAIM_SERIALIZER_CLASS)
    serializer = LoginSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
        mfa = serializer.validated_data.get("mfa", False)
        refresh_token = serializer.validated_data.get("refresh_token", "")
        access_token = serializer.validated_data.get("access_token", "")
        user = serializer.validated_data.get("user", None)
        email_verified = serializer.validated_data.get("email_verified", False)

        # Handle response based on email verification and MFA
        if not email_verified:
            response_data = {
                "email": user.email,
                "msg": Messages.status_unverified,
                "code": "email_unverified",
            }
            response_status = status.HTTP_200_OK
        elif mfa:
            response_data = {"mfa": user.id}
            response_status = status.HTTP_200_OK
            response = Response(response_data, status=response_status)
            response = set_cookies(mfa=user.id, response=response)
            response = reset_response(response)
            return response
        else:
            response_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": USER_CLAIM_SERIALIZER(user).data,
            }
            response_status = status.HTTP_200_OK

        response = Response(response_data, status=response_status)
        response = set_cookies(
            response=response, access_token=access_token, refresh_token=refresh_token
        )
        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    refresh_token = request.data.get("refresh_token") or request.COOKIES.get(
        accounts_config.REFRESH_TOKEN_COOKIE
    )

    if not refresh_token:
        return Response(
            {"msg": Messages.token_error}, status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        tokens = generate_tokens(request.user, refresh_token=refresh_token)
        response = Response(
            {"access_token": tokens["access_token"]}, status=status.HTTP_200_OK
        )
        new_response = set_cookies(
            access_token=tokens["access_token"], response=response
        )
        return new_response
    except TokenError:
        return Response(
            {"msg": Messages.token_error}, status=status.HTTP_401_UNAUTHORIZED
        )

    except Exception:
        return Response(
            {"msg": Messages.general_msg}, status=status.HTTP_400_BAD_REQUEST
        )


class ResendEmail(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Collect email from the user to resend the verification email.
        """
        serializer = ResendVerificationEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.save()
            return Response(
                {"email": email, "msg": Messages.email_sent},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


resend_verification_email = ResendEmail.as_view()


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify email
    """
    serializer = VerifyEmailSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        return Response(
            {"email": email, "msg": Messages.status_verified}, status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    SignupSerializer = get_serializer(accounts_config.REGISTRATION_SERIALIZER_CLASS)
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        response = Response(
            {
                "email": user.email,
                "msg": Messages.status_unverified,
            },
            status=status.HTTP_201_CREATED,
        )

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enable_mfa(request):
    user = request.user
    try:
        account_mfa, created = MultiFactorAuth.objects.get_or_create(account=user)

        if not account_mfa.secret_key:
            # Ensure the generated key is unique
            unique_key_generated = False
            while not unique_key_generated:
                potential_key = pyotp.random_base32()
                if not MultiFactorAuth.objects.filter(
                    secret_key=potential_key
                ).exists():
                    account_mfa.secret_key = potential_key
                    unique_key_generated = True

        # Generate the OTP provisioning URI
        otp_url = pyotp.TOTP(
            account_mfa.secret_key, digits=accounts_config.MFA_CODE_DIGITS
        ).provisioning_uri(user.username, issuer_name=accounts_config.MFA_ISSUER_NAME)

        account_mfa.save()

        return Response(
            {"url": otp_url, "key": account_mfa.secret_key}, status=status.HTTP_200_OK
        )
    except MultiFactorAuth.DoesNotExist:
        return Response(
            {"msg": Messages.mfa_not_activated},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        return Response(
            {"msg": Messages.general_msg},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_mfa(request):
    user = request.user
    try:
        mfa_account = MultiFactorAuth.objects.get(account=user)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})
    if mfa_account.activated:
        return Response(
            {"msg": Messages.mfa_already_activated}, status=status.HTTP_200_OK
        )

    serializer = MfaCodeSerializer(data=request.data)

    if serializer.is_valid():
        code = serializer.validated_data.get("code")
        totp = pyotp.TOTP(mfa_account.secret_key)

        if totp.verify(code):
            mfa_account.activated = True
            mfa_account.set_recovery_codes()
            mfa_account.save()
            return Response(
                {"msg": Messages.mfa_enabled_success}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"msg": Messages.mfa_invalid_otp}, status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mfa_status(request):
    user = request.user
    try:
        mfa_account = MultiFactorAuth.objects.get(account=user)
        return Response(
            data={
                "mfa_status": mfa_account.activated,
                "recovery_codes": mfa_account.recovery_codes,
            },
            status=status.HTTP_200_OK,
        )
    except MultiFactorAuth.DoesNotExist:
        return Response(
            data={"mfa_status": False, "recovery_codes": []},
            status=status.HTTP_200_OK,
        )
    except Exception:
        return Response(
            data={"msg": Messages.general_msg},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def regenerate_recovery_codes(request):
    user = request.user
    try:
        # Retrieve the MultiFactorAuth instance
        mfa_account = MultiFactorAuth.objects.get(account=user)

        if not mfa_account.activated:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": Messages.mfa_not_activated},
            )

        # Generate new recovery codes
        mfa_account.set_recovery_codes()
        mfa_account.save()
        if accounts_config.MFA_EMAIL_ALERTS_ENABLED:
            handle_email_mechanism(
                subject=Messages.mfa_code_generated_email_subject,
                email=user.email,
                template="regenerate_codes",
                context={
                    "username": user.username,
                    "email": user.email,
                    "time": timezone.now(),
                    "ip_address": get_client_ip(request),
                    "user_agent": get_user_agent(request),
                },
            )
        return Response(
            status=status.HTTP_200_OK,
            data={"msg": Messages.mfa_recovery_codes_generated},
        )
    except MultiFactorAuth.DoesNotExist:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"msg": Messages.mfa_not_activated},
        )
    except Exception:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"msg": Messages.general_msg},
        )


class DeactivateMfaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DeactivateMfaSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": Messages.mfa_deactivated}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    AccountSerializer = get_serializer(accounts_config.USER_DETAIL_SERIALIZER_CLASS)
    user = request.user
    serializer = AccountSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    serializer = LogoutSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        try:
            serializer.save()
        except Exception:
            return Response(
                {"msg": Messages.general_msg}, status=status.HTTP_400_BAD_REQUEST
            )

        logout(request)

        response = Response(
            {"msg": Messages.logout_successful}, status=status.HTTP_200_OK
        )

        for cookie in request.COOKIES:
            response.delete_cookie(cookie)

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def mfa_login(request):
    user_id = request.COOKIES.get(accounts_config.MFA_COOKIE_NAME)
    User_Claim_Serializer = get_serializer(accounts_config.USER_CLAIM_SERIALIZER_CLASS)
    refresh = None
    access = None
    if not user_id:
        return Response(
            {
                "msg": Messages.invalid_account,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = Account.objects.get(pk=user_id)
        mfa_account = MultiFactorAuth.objects.get(account=user)
    except Account.DoesNotExist:
        return Response(
            {"msg": Messages.invalid_account}, status=status.HTTP_400_BAD_REQUEST
        )

    if not mfa_account.activated:
        return Response(
            {"msg": Messages.mfa_not_activated},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = request.data.get("code", 0)
    totp = pyotp.TOTP(mfa_account.secret_key)

    if totp.verify(code):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

    elif code in mfa_account.recovery_codes:
        # Recovery code is valid
        mfa_account.recovery_codes.remove(code)  # Remove used recovery code
        mfa_account.save()
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
    else:
        return Response(
            {"msg": Messages.mfa_invalid_otp}, status=status.HTTP_400_BAD_REQUEST
        )

    update_last_login(None, user)
    user_logged_in.send(
        sender=user.__class__,
        request=request,
        user=user,
    )

    response = Response(
        {
            "refresh": str(refresh),
            "access": str(access),
            "user": User_Claim_Serializer(user).data,
        },
        status=status.HTTP_200_OK,
    )

    response = set_cookies(
        response=response, access_token=access, refresh_token=refresh
    )
    response.delete_cookie(accounts_config.MFA_COOKIE_NAME)

    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    if request.user.is_authenticated:
        return Response(
            {"msg": Messages.already_authenticated},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        reset_code = serializer.save()
        return Response(
            {
                "msg": Messages.password_reset_code_sent,
                "attempts": reset_code.attempts,
                "email": reset_code.email,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_reset_password(request):
    serializer = VerifyResetPasswordSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"msg": Messages.password_reset_successful},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
