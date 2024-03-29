from .views import (
    create_post,
    posts,
    like_post,
    dislike_post,
    post_detail,
    get_post_image,
    get_accounts_to_tag,
    search,
    ping_server,
    comments,
    create_comment,
    delete_post,
    get_notifications,
)
from django.urls import path

urlpatterns = [
    path("compose/", create_post, name="compose"),
    path("ping/", ping_server),
    path("posts/", posts, name="posts"),
    path("like/<int:pk>/<str:type>/", like_post),
    path("unlike/<int:pk>/<str:type>/", dislike_post),
    path("post/<int:pk>/", post_detail, name="post"),
    path("post/images/<int:pk>/", get_post_image),
    path("s/accounts/", get_accounts_to_tag),
    path("search/", search, name="search"),
    path("post/comments/<int:pk>/", comments),
    path("comment/", create_comment),
    path("post/delete/<int:pk>/", delete_post),
    path("notifications/", get_notifications),
]
