from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.urls import reverse


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
    phone = models.CharField(max_length=12, null=True, blank=True, unique=True)
    gender = models.CharField(
        max_length=10, blank=True, null=True, choices=GENDER_OPTIONS
    )
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
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
    username_last_update = models.DateTimeField(blank=True, null=True)
    last_location = models.CharField(max_length=255, blank=True, null=True)
    cover_image = models.ImageField(upload_to="profile_covers/", blank=True, null=True)
    cover_image_hash = models.CharField(blank=True, null=True, max_length=200)

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

        else:
            return None

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True

    def get_absolute_url(self):
        return reverse("account", kwargs={"username": self.username})

    class Meta:
        ordering = ["-id"]
