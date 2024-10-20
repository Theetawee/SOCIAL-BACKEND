from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account, Follow

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
admin.site.register(Follow)
