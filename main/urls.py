from .views import search,ping
from django.urls import path

urlpatterns=[
    path("search/",search),
    path('ping/',ping),
]
