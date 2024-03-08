from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):

    def render_mail(
        self,
        template_prefix,
        email,
        context,
        headers={"Content-Type": "text/plain"},
    ):
        return super().render_mail(template_prefix, email, context, headers)

    def get_from_email(self):
        return "accounts@waanverse.com"

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import (
            user_email,
            user_field,
            user_username,
        )

        data = form.cleaned_data
        name = data.get("name")
        email = data.get("email")
        username = data.get("username")
        user_email(user, email)
        user_username(user, username)
        if name:
            user_field(user, "name", name)
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def send_mail(self, template_prefix, email, context):
        try:
            context["activate_url"] = (
                settings.EMAIL_VERIFICATION_URL + "activate/" + context["key"] + "/"
            )

        except KeyError:
            pass
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
