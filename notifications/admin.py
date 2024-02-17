from django.contrib import admin
from .models import PushInformation,SubscriptionInfo,Notification
# Register your models here.


admin.site.register(PushInformation)
admin.site.register(Notification)
admin.site.register(SubscriptionInfo)
