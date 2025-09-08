from django.db import models
from django.conf import settings

class MediaAsset(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kind = models.CharField(max_length=10, choices=[("image","image"),("video","video")])
    file = models.FileField(upload_to="user_uploads/")
    thumbnail = models.ImageField(upload_to="thumbnails/")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) 
     