from django.urls import path

from .views import (
    account_interactions,
    basic_user_info,
    update_profile,
    user_account_action,
    user_detail,
    user_list,
)

urlpatterns = [
    path("users", user_list, name="user_list"),
    path("users/<str:username>", user_detail, name="user_detail"),
    path("update", update_profile, name="update"),
    path("peep/<str:username>", basic_user_info, name="peep"),
    path("action/<str:action>/<str:username>", user_account_action, name="follow_user"),
    path(
        "interactions/<str:interaction_type>/<str:username>",
        account_interactions,
        name="account_interactions",
    ),
]
