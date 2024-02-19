from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from phonenumber_field.modelfields import PhoneNumberField
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from django.contrib.humanize.templatetags.humanize import naturalday


from django.db.models.signals import post_save
import blurhash
from PIL import Image


class AccountManager(BaseUserManager):
    def create_user(self, email, username, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Please enter your email")
        if not username:
            raise ValueError("Please enter your username")
        if not name:
            raise ValueError("Please enter your name")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, name=name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, name, password, **extra_fields)


class Friendship(models.Model):
    account1 = models.ForeignKey(
        "Account", on_delete=models.CASCADE, related_name="friendships_as_account1"
    )
    account2 = models.ForeignKey(
        "Account", on_delete=models.CASCADE, related_name="friendships_as_account2"
    )
    date_started = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("acquaintance", "Acquaintance"),
            ("close_friend", "Close Friend"),
            ("best_friend", "Best Friend"),
        ],
        default="acquaintance",
    )
    is_one_sided = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.account1.username} - {self.account2.username}"


class Badge(models.Model):
    name = models.CharField(max_length=255)
    badge_image = models.ImageField(upload_to="badges/")
    description = models.TextField()
    value = models.DecimalField(max_digits=10, decimal_places=1)
    image_hash = models.CharField(
        max_length=255, default="L02v:alCD4fRlCk[Z2Z28wf5HXaI"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def image(self):
        if self.badge_image:
            return self.badge_image.url
        else:
            return None

    @property
    def added_on(self):
        return naturalday(self.created_at)

    @property
    def updated_on(self):
        return naturalday(self.updated_at)


class Account(AbstractBaseUser, PermissionsMixin):
    GENDER_OPTIONS = (
        ("male", "male"),
        ("female", "female"),
        ("other", "other"),
    )
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True, verbose_name="Email")
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    gender = models.CharField(
        max_length=10, blank=True, null=True, choices=GENDER_OPTIONS
    )
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    profile_url = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date joined")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Last login")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    location = models.CharField(max_length=20, blank=True, null=True)
    badges = models.ManyToManyField(Badge, blank=True)
    profile_image_hash = models.CharField(
        max_length=255, default="LTL55tj[~qof?bfQIUj[j[fQM{ay"
    )
    friends = models.ManyToManyField(
        "self", through=Friendship, symmetrical=False, blank=True
    )
    username_last_update = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "email"]

    objects = AccountManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.username

    @property
    def joined(self):
        return naturalday(self.date_joined)

    @property
    def image(self):
        if self.profile_image:
            url = self.profile_image.url
            return url
        elif self.profile_url:
            return self.profile_url
        else:
            return None

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True


class FriendRequest(models.Model):
    STATUS = (
        ("pending", "pending"),
        ("accepted", "accepted"),
        ("declined", "declined"),
    )
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="recipient"
    )

    date_sent = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    def __str__(self):
        return f"{self.sender} sent request to {self.recipient}"


@receiver(user_signed_up)
def social_account_signed_up(request, user, **kwargs):
    try:
        social_account = SocialAccount.objects.get(user=user)
        extra_data = social_account.extra_data.get("picture")
        names = social_account.extra_data.get("name")
        username = social_account.extra_data.get("given_name")
        user.username = username.lower()
        user.name = names
        user.profile_url = extra_data
        user.save()
    except:
        pass


@receiver(post_save, sender=Badge)
def create_image_hash(sender, instance, created, **kwargs):
    if created:
        if instance.badge_image:
            with Image.open(instance.badge_image) as image:
                image.thumbnail((100, 100))
                hash = blurhash.encode(image, x_components=4, y_components=3)
                instance.image_hash = hash
                instance.save()
