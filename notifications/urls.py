from django.urls import path
from .views import save_info,notifications,notifications_seen

urlpatterns=[
    path('save/',save_info),
    path('',notifications),
    path('seen/<int:pk>/',notifications_seen)
]
