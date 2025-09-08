from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance,created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={
            "display_name": instance.display_name or instance.email.split("@")[0]
        })


        