from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import secrets   # we use this to generate secure random codes and tokens


# This manager controls how users are created in our custom User model
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # This function creates a normal user (not an admin)

        # Ensure email is provided, because our system uses email instead of username
        if not email:
            raise ValueError("Email is required")

        # Normalize email (e.g., make lowercase domain part)
        email = self.normalize_email(email)

        # Create a new user instance using the given fields
        user = self.model(email=email, **extra_fields)

        # Securely set the password (hashing it)
        if password:
            user.set_password(password)
        else:
            # If no password, mark it as unusable
            user.set_unusable_password()

        # Save the user in the database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # This function creates an admin user (superuser)

        # Ensure required flags for admin are set
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Call create_user with admin privileges
        return self.create_user(email, password, **extra_fields)


# This is our custom User model
class User(AbstractBaseUser, PermissionsMixin):
    # The main identifier is email, not username
    email = models.EmailField(unique=True)   # must be unique for every user
    phone = models.CharField(max_length=20, blank=True, null=True)  # optional phone number
    display_name = models.CharField(max_length=50, blank=True)      # name shown to other users
    dob = models.DateField(blank=True, null=True)                   # date of birth
    gender = models.CharField(max_length=20, blank=True)            # gender of the user
    seeking = models.CharField(max_length=20, blank=True)           # preference of partner

    # Verification flags
    email_verified = models.BooleanField(default=False)  # set to True when user verifies email
    phone_verified = models.BooleanField(default=False)  # set to True when user verifies phone

    # Two-factor authentication
    twofa_enabled = models.BooleanField(default=False)   # True if 2FA is enabled
    twofa_secret = models.CharField(max_length=64, blank=True, null=True)  # secret key for TOTP

    # Django required fields
    is_active = models.BooleanField(default=True)   # can login if True
    is_staff = models.BooleanField(default=False)   # can access admin site if True
    date_joined = models.DateTimeField(default=timezone.now)  # auto set when created

    # Tell Django to use email instead of username for login
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no extra fields required for createsuperuser

    # Attach the custom manager
    objects = UserManager()

    def __str__(self):
        # Display email when object is printed
        return self.email


# This model is used to store OTP codes for phone/email verification
class OtpCode(models.Model):
    target = models.CharField(max_length=255)   # phone number or email that receives the OTP
    purpose = models.CharField(max_length=20)   # why OTP was generated (e.g., "phone_verify")
    code = models.CharField(max_length=6)       # 6 digit code like 123456
    expires_at = models.DateTimeField()         # when OTP becomes invalid
    attempts = models.PositiveIntegerField(default=0)  # how many times user tried wrong OTP
    created_at = models.DateTimeField(auto_now_add=True)  # auto fill when created

    @classmethod
    def issue(cls, target: str, purpose: str, ttl_minutes: int = 5):
        # This function generates a new OTP and stores it in the database
        # Generate a random 6-digit number padded with zeros if needed
        code = f"{secrets.randbelow(1_000_000):06d}"

        # Save OTP record with an expiry time (default 5 minutes)
        return cls.objects.create(
            target=target,
            purpose=purpose,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
        )

    def is_expired(self):
        # Check if OTP has passed its expiry time
        return timezone.now() >= self.expires_at


# This model stores tokens used for verifying a user's email
class EmailVerifyToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")  
    # Each token belongs to a user, and if the user is deleted, the tokens are deleted too

    token = models.CharField(max_length=64, unique=True)   # unique random token string
    expires_at = models.DateTimeField()                    # expiry time (default 24h)
    created_at = models.DateTimeField(auto_now_add=True)   # auto fill when token is created

    @classmethod
    def new_for(cls, user, ttl_hours: int = 24):
        # This function generates a new verification token for a user
        # Generate a secure random token
        token = secrets.token_urlsafe(32)

        # Create and save token with expiry time
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=ttl_hours),
        )

    def is_expired(self):
        # Check if the token has expired
        return timezone.now() >= self.expires_at
