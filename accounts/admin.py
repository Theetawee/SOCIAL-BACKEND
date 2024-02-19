from django.contrib import admin
from .models import Account,Badge,FriendRequest,Friendship,Hobby
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class AccountAdmin(UserAdmin):
    list_display = (
        "email",
        "is_active",
        "is_staff",
        "name",
        "username",
        "last_login",
        "date_joined",
    )
    search_fields = ("email", "name", "username")
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(Hobby)
admin.site.register(Friendship)
admin.site.register(FriendRequest)

admin.site.register(Badge)
