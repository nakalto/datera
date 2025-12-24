from django.db import models
from django.conf import settings

class Profile(models.Model):
    # Link profile to user account (one-to-one relationship)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Basic personal info
    full_name = models.CharField(max_length=100, blank=True, null=True)

    # Gender of the user (choices for clarity)
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    gender = models.CharField(
        max_length=1,                # only store "M" or "F"
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    # Birthday field
    birthday = models.DateField(blank=True, null=True)

    # Short biography
    bio = models.TextField(blank=True, null=True)

    # Flag to mark if onboarding is complete
    onboarding_complete = models.BooleanField(default=False)

    # Relationship goals (Tinder-style categories)
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
        blank=True,
        null=True,
        help_text="User's dating or social intention (Explore categories)"
    )

    # Preference: who the user is looking for (men, women, or all)
    LOOKING_FOR_CHOICES = [
        ("M", "Men"),
        ("F", "Women"),
        ("A", "All"),
    ]
    looking_for = models.CharField(
        max_length=10,                # only store "M", "F", or "A"
        choices=LOOKING_FOR_CHOICES,
        default="A",
        help_text="Who the user wants to see in dashboard"
    )

    def __str__(self):
        # Show full name if available, otherwise username
        return f"{self.full_name or self.user.username}'s Profile"


class UserPhoto(models.Model):
    # Link photo to profile (many-to-one relationship)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="photos")

    # Actual image file (stored in MEDIA_ROOT/user_photos/)
    image = models.ImageField(upload_to="user_photos/")

    # Timestamp when photo was uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Display username and photo ID for clarity
        return f"{self.profile.user.username} - Photo {self.id}"
