from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    # Phone number field (unique, optional)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Verification flags
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=50, default='login')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    consumed = models.BooleanField(default=False)

    def is_valid(self):
        return (
            timezone.now() < self.expires_at
            and self.attempts < 5
            and not self.consumed
        )

    def __str__(self):
        return f"OTP for {self.user.username} ({self.purpose})"
