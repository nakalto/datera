from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
class User(AbstractUser):
    # Phone number field (unique, optional)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Flags to track verification status
    email_verified = models.BooleanField(default=False)  # track if email is verified
    phone_verified = models.BooleanField(default=False)  # track if phone is verified

    # Define username field (default is 'username')
    USERNAME_FIELD = 'username'

    # Required fields when creating a superuser
    REQUIRED_FIELDS = ['email']


# OTP model to store one-time codes for login/verification
class OTP(models.Model):
    # Link OTP to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Purpose of OTP (e.g., 'login', 'password_reset')
    purpose = models.CharField(max_length=50, default='login')

    # The actual 6-digit code
    code = models.CharField(max_length=6)

    # Timestamp when OTP was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Expiry timestamp (e.g., 5 minutes after creation)
    expires_at = models.DateTimeField()

    # Number of times user attempted to enter this OTP
    attempts = models.IntegerField(default=0)

    # Flag to mark if OTP has been used successfully
    consumed = models.BooleanField(default=False)

    # Helper method to check if OTP is still valid
    def is_valid(self):
        """
        OTP is valid if:
        - Current time is before expiry
        - Attempts are fewer than 5
        - OTP has not been consumed
        """
        return (timezone.now() < self.expires_at and self.attempts < 5 and not self.consumed)
