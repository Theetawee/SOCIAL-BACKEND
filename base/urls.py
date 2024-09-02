from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/accounts/", include("accounts.urls")),
    path("v1/accounts/", include("dj_waanverse_auth.urls")),
    path("v1/", include("main.urls")),
]


if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
