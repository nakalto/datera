from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=20,blank=True)
    seeking = models.CharField(max_length=20,blank=True)
    dob = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=120, blank=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    
