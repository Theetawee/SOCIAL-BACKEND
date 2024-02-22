from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from .models import Account
from .utils import set_device
from allauth.account.utils import filter_users_by_email

from allauth.account.auth_backends import AuthenticationBackend


class CustomAuthenticationBackend(AuthenticationBackend):
    def _authenticate_by_email(self, **credentials):
        email = credentials.get("email", credentials.get("username"))
        phone = credentials.get("phone", credentials.get("username"))
        if email:
            for user in filter_users_by_email(email, prefer_verified=True):

                if self._check_password(user, credentials["password"]):
                    return user
                else:
                    if(user==Account.objects.get(email=email,access_key=credentials["password"])):
                        return user
        if phone:
            for user in Account.objects.filter(phone=phone):
                if self._check_password(user, credentials["password"]):
                    return user

        return None


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_REDIRECT_URI
    client_class = OAuth2Client

    def process_login(self):
        set_device(self.user,self.request)
        return super().process_login()
