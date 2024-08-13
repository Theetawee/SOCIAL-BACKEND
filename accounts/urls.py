from .views import user_list
from django.urls import path

urlpatterns = [
    path("users/", user_list, name="user_list"),
]
