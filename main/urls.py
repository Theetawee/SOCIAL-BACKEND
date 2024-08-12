from django.urls import path

from .views import (
    comment_list,
    create_post,
    post_action,
    post_detail,
    post_list,
    register_post_view,
)

urlpatterns = [
    path("posts/", post_list, name="post_list"),
    path("posts/create", create_post, name="create_post"),
    path("posts/comment/<int:post_id>", create_post, name="create_post_comment"),
    path("posts/<int:pk>", post_detail, name="post_detail"),
    path("posts/<int:pk>/comments", comment_list, name="comment_list"),
    path("posts/action/<str:action>/<int:post_id>", post_action, name="post_action"),
    path("posts/views/<int:post_id>", register_post_view, name="post_view"),
]
