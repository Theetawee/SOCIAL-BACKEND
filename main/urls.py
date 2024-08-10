from .views import PostViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Initialize the router
router = DefaultRouter()

# Register the PostViewSet with the router
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
