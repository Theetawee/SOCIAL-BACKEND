import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.templatetags.static import static
from django.urls import reverse


class AccountManager(BaseUserManager):
    def create_user(self, email, username, name=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Please enter your email")
        if not username:
            raise ValueError("Please enter your username")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, name=name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email, name=None, password=None, **extra_fields
    ):
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
    name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True, verbose_name="Email")
    phone = models.CharField(max_length=12, null=True, blank=True, unique=True)
    gender = models.CharField(
        max_length=10, blank=True, null=True, choices=GENDER_OPTIONS
    )
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date joined")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Last login")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    verified_company = models.BooleanField(default=False)
    location = models.CharField(max_length=20, blank=True, null=True)
    badges = models.ManyToManyField(
        "Badge", blank=True
    )  # Assuming Badge is defined elsewhere
    profile_image_hash = models.CharField(
        max_length=255, default="LTL55tj[~qof?bfQIUj[j[fQM{ay"
    )
    username_last_update = models.DateTimeField(blank=True, null=True)
    last_location = models.CharField(max_length=255, blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    cover_image_hash = models.CharField(blank=True, null=True, max_length=200)
    google_account = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)

    referral_code = models.CharField(max_length=255, blank=True, unique=True, null=True)
    referred_accounts = models.ManyToManyField("self", blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = AccountManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name or self.username

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)

    def generate_referral_code(self):
        """Generate a unique referral code."""
        code = None
        while not code or Account.objects.filter(referral_code=code).exists():
            code = str(uuid.uuid4()).replace("-", "")[
                :10
            ]  # Generate a 10-character unique code
        return code

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True

    def get_image(self):
        if self.profile_image_url:
            return self.profile_image_url
        else:
            return static("images/default.webp")

    def get_absolute_url(self):
        return reverse("account", kwargs={"username": self.username})

    def follow(self, user):
        """Follow a user."""
        if not self.is_following(user):
            if user != self:
                Follow.objects.create(follower=self, following=user)

    def unfollow(self, user):
        """Unfollow a user."""
        Follow.objects.filter(follower=self, following=user).delete()

    def is_following(self, user):
        """Check if the user is following another user."""
        return Follow.objects.filter(follower=self, following=user).exists()

    def get_following(self):
        """Get the list of users this user is following."""
        return Account.objects.filter(
            accounts_followers__follower=self
        )  # Updated related_name

    def get_followers(self):
        """Get the list of accounts following this account."""
        return Account.objects.filter(
            accounts_following__following=self
        )  # Updated related_name

    @property
    def is_verified_account(self):
        return self.verified or self.verified_company

    class Meta:
        ordering = ["-id"]


class Follow(models.Model):
    follower = models.ForeignKey(
        Account,
        related_name="accounts_following",  # Changed to avoid conflict with main app
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        Account,
        related_name="accounts_followers",  # Changed to avoid conflict with main app
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower} follows {self.following}"
