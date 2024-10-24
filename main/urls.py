from django.urls import path

from .views import (
    account_post_list,
    comment_list,
    create_post,
    delete_action,
    get_feedback,
    ping,
    post_action,
    post_detail,
    post_list,
    register_post_view,
    search_view,
    set_reaction,
)

urlpatterns = [
    path("ping", ping, name="ping"),
    path("posts/", post_list, name="post_list"),
    path("posts/create", create_post, name="create_post"),
    path("posts/comment/<int:post_id>", create_post, name="create_post_comment"),
    path("posts/<int:pk>", post_detail, name="post_detail"),
    path("posts/<int:pk>/comments", comment_list, name="comment_list"),
    path("posts/action/<str:action>/<int:post_id>", post_action, name="post_action"),
    path("posts/views/<int:post_id>", register_post_view, name="post_view"),
    path("search", search_view, name="search"),
    path("feedback", get_feedback, name="feedback"),
    path("delete/<int:post_id>", delete_action, name="delete_action"),
    path("post/react/<int:post_id>", set_reaction, name="set_reaction"),
    path("account/posts", account_post_list, name="account_post_list"),
]
