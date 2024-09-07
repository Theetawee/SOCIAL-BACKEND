from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .views import PostSitemap

sitemaps = {"posts": PostSitemap}


urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    )
]
