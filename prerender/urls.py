from django.urls import path

from .views import index, profile_view

urlpatterns = [
    path("", index, name="pre_home"),
    path("<str:username>", profile_view, name="profile"),
]
