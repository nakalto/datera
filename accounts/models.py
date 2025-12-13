from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Phone number field (unique, optional)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Onboarding fields (Tinder style)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/photos/", null=True, blank=True)

    # Track onboarding completion
    onboarding_complete = models.BooleanField(default=False)

    # Verification flags
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Relationship goal field (Tinder-style categories)
    RELATIONSHIP_GOALS = [
        ("longterm", "Long-term partner"),   # 🌹
        ("serious", "Serious daters"),       # 🦢
        ("freetonight", "Free tonight"),     # 🌙
        ("shortterm", "Short-term fun"),     # 🎉
        ("friendship", "Friendship"),        # 🤝
        ("unsure", "Not sure yet"),          # ❓
    ]
    relationship_goal = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_GOALS,
        null=True,
        blank=True,
        help_text="User's dating or social intention (Explore categories)"
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.full_name or self.username

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
