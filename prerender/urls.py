from django.urls import path

from .views import index, login_view, post_detail_view, profile_view

urlpatterns = [
    path("", index, name="pre_home"),
    path("status/<int:post_id>", post_detail_view, name="pre_post_detail"),
    path("<str:username>", profile_view, name="profile"),
    path("i/login", login_view, name="pre_login"),
]
