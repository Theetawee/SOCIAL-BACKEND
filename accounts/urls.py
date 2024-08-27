from django.urls import path

from .views import GoogleAuthCallbackView, google_url, user_list

urlpatterns = [
    path("users/", user_list, name="user_list"),
    path("google_url", google_url, name="google_url"),
    path("google/callback", GoogleAuthCallbackView.as_view(), name="google_callback"),
]
