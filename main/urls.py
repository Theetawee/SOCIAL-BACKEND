from django.urls import path
from .views import homepage, ArticleDetail

urlpatterns = [
    path("", homepage, name="index"),
    path("article/<slug:slug>/", ArticleDetail.as_view()),
]
