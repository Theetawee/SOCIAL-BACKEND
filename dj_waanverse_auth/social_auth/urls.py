from django.urls import path

from .views import GoogleAuthCallbackView, google_url

urlpatterns = [
    path("url", google_url, name="google_url"),
    path("callback", GoogleAuthCallbackView.as_view(), name="google_callback"),
]
