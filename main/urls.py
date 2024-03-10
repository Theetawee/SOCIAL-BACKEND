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
)
from django.urls import path

urlpatterns = [
    path("compose/", create_post),
    path("ping/", ping_server),
    path("posts/", posts),
    path("like/<int:pk>/<str:type>/", like_post),
    path("unlike/<int:pk>/<str:type>/", dislike_post),
    path("post/<int:pk>/", post_detail),
    path("post/images/<int:pk>/", get_post_image),
    path("s/accounts/", get_accounts_to_tag),
    path("search/", search),
]
