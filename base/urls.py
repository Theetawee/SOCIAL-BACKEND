from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("dj_rest_auth.urls")),
    path("", include("main.urls")),
    path('n/',include('notifications.urls')),
    path('posts/',include('posts.urls')),
    path('plus/',include('plus.urls')),
    path('savelog/',include('savelog.urls'))
]
if settings.DEBUG:
    urlpatterns+=path("__debug__/", include("debug_toolbar.urls")),

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
