from django.urls import path
from .views import notifications,notifications_seen

urlpatterns=[
    path('',notifications),
    path('seen/<int:pk>/',notifications_seen)
]
