from django.contrib.sitemaps import Sitemap
from main.models import Post
from django.urls import reverse
from accounts.models import Account


class CustomSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1

    def items(self):
        custom_urls = ["/home", "/accounts/login", "/accounts/signup"]

        return custom_urls

    def location(self, obj):
        return obj


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):

        return f"/posts/{obj.pk}"


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1

    def items(self):
        return [
            "compose",
        ]

    def location(self, item):
        return reverse(item)


class AccountSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Account.objects.all()

    def lastmod(self, obj):
        return obj.last_login

    def location(self, obj):
        
        return f"/{obj.username}"
