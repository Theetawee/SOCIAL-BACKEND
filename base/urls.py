from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("v1/accounts/", include("accounts.urls")),
    path("v1/accounts/", include("dj_waanverse_auth.urls")),
    path("v1/", include("main.urls")),
    path("prerender/", include("prerender.urls")),
]

if settings.ADMIN_ENABLED:
    urlpatterns += [
        path(f"{settings.ADMIN_URL}/", admin.site.urls),
    ]

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
