from .views import post_list, create_post, post_detail
from django.urls import path


urlpatterns = [
    path("posts/", post_list, name="post_list"),
    path("posts/create", create_post, name="create_post"),
    path("posts/<int:pk>", post_detail, name="post_detail"),
]
