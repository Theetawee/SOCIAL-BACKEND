from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .views import AccountSitemap, PostSitemap, StaticSitemap

sitemaps = {"posts": PostSitemap, "static": StaticSitemap, "accounts": AccountSitemap}


urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    )
]
