from django.db import models
from django.conf import settings

# Link Profile to your custom User model
class Profile(models.Model):
    # One-to-one relationship: each user has exactly one profile
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Onboarding fields
    name = models.CharField(max_length=100, blank=True, null=True)       # Step 1
    gender = models.CharField(max_length=20, blank=True, null=True)      # Step 2
    birthday = models.DateField(blank=True, null=True)                   # Step 3
    bio = models.TextField(blank=True, null=True)                        # Step 4
    photo = models.ImageField(upload_to='profiles/photos/', blank=True, null=True)  # Step 5

    # Track onboarding completion
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}"




