from django.urls import path

from .views import user_detail, user_list

urlpatterns = [
    path("users/", user_list, name="user_list"),
    path("users/<str:username>", user_detail, name="user_detail"),
]
