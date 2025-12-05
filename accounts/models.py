from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone 

class User(AbstractUser):
    phone = models.CharField(max_length=20,unique=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False) #track if email is verified 
    phone_verified = models.BooleanField(default=False) #track if phone is verified

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, default='login')
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    consumed = models.BooleanField(default=False) #Whether OTP has been used


    def is_valid(self):
        return (timezone.now() < self.expire_at and self.attempts < 5 and not self.consumed)  