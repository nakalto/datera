# Import Django's base model class
from django.db import models

# Import your custom User model from the accounts app
from accounts.models import User

# Import slugify utility (useful for future extensions like tags or reactions)
from django.utils.text import slugify
from django.shortcuts import render

from django.utils import timezone

# Define the Swipe model to record likes/dislikes between users
class Swipe(models.Model):
    # User who performs the swipe (like or dislike)
    from_user = models.ForeignKey(
        User,
        related_name="swipes_made",   # allows reverse lookup: user.swipes_made.all()
        on_delete=models.CASCADE      # delete swipes if user is deleted
    )

    # User who was swiped on
    to_user = models.ForeignKey(
        User,
        related_name="swipes_received",  # allows reverse lookup: user.swipes_received.all()
        on_delete=models.CASCADE         # delete swipes if user is deleted
    )

    # Boolean field: True = like, False = dislike
    is_like = models.BooleanField()

    # Timestamp when the swipe happened (auto-filled by Django)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional reaction field for advanced interactions (emoji, tag, etc.)
    reaction = models.CharField(max_length=16, blank=True)

    # Meta options for the Swipe model
    class Meta:
        # Ensure a user can only swipe another user once (no duplicates)
        unique_together = ("from_user", "to_user")

    # Override the save method to add custom logic
    def save(self, *args, **kwargs):
        # Call the original save method to store the swipe
        super().save(*args, **kwargs)

        # Only check for matches if this swipe is a like
        if self.is_like:
            # Look for a reciprocal like from the other user
            reciprocal = Swipe.objects.filter(
                from_user=self.to_user,
                to_user=self.from_user,
                is_like=True
            ).exists()

            # If reciprocal like exists, create a Match automatically
            if reciprocal:
                # Normalize ordering (smaller ID first) to prevent duplicate matches
                user1, user2 = sorted([self.from_user, self.to_user], key=lambda u: u.id)
                Match.objects.get_or_create(user1=user1, user2=user2)

    # String representation for debugging/admin
    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({'Like' if self.is_like else 'Dislike'})"


# Define the Match model to store mutual likes
class Match(models.Model):
    # First user in the match
    user1 = models.ForeignKey(
        User,
        related_name="matches_initiated",   # reverse lookup: user.matches_initiated.all()
        on_delete=models.CASCADE
    )

    # Second user in the match
    user2 = models.ForeignKey(
        User,
        related_name="matches_received",    # reverse lookup: user.matches_received.all()
        on_delete=models.CASCADE
    )

    # Timestamp when the match was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Meta options for the Match model
    class Meta:
        # Prevent duplicate matches (same pair stored twice)
        unique_together = ("user1", "user2")

    # String representation for debugging/admin
    def __str__(self):
        return f"Match: {self.user1} ❤️ {self.user2}"


class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_given")
    liked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_received")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("liker", "liked")
