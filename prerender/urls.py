from django.urls import path

from .views import index, login_view, profile_view

urlpatterns = [
    path("", index, name="pre_home"),
    path("<str:username>", profile_view, name="profile"),
    path("i/login", login_view, name="pre_login"),
]
