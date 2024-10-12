from rest_framework import status

from .settings import accounts_config


class CookiesHandlerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        try:
            if (response.data["code"]) == "user_not_found" or (
                response.status_code == status.HTTP_401_UNAUTHORIZED
            ):
                response.delete_cookie(accounts_config.ACCESS_TOKEN_COOKIE)
                response.delete_cookie(accounts_config.REFRESH_TOKEN_COOKIE)

        except Exception:
            pass
        return response
