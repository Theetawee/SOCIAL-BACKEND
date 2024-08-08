from .views import post_list
from django.urls import path

urlpatterns = [
    path("", post_list, name="post_list"),
]
