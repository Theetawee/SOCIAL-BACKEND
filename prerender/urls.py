from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .sitemap import AccountSitemap, PostSitemap, StaticSitemap
from .views import (
    index,
    login_view,
    post_detail_view,
    profile_view,
    search_view,
    signup_view,
)

sitemaps = {"posts": PostSitemap, "static": StaticSitemap, "accounts": AccountSitemap}


urlpatterns = [
    path("", index, name="pre_home"),
    path("search", search_view, name="pre_search"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("status/<int:post_id>", post_detail_view, name="pre_post"),
    path("<str:username>", profile_view, name="pre_profile"),
    path("i/login", login_view, name="pre_login"),
    path("i/signup", signup_view, name="pre_signup"),
]
