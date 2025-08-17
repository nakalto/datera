from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager
from django.utils import timezone
from datetime import timedelta
import secrets

class UserManager(BaseUserManager):
    #Create a regular user with emails as the unique identifier
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
          user.set_password(password)
        else: 
            user.set_unusable_password() 
        user.save(using=self._db)
        return user
    
    #create a superuser with all permission 
    def create_superuser(self, email,password=None, **extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("superuser must have is_staff=True")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("super user must have is_superuser=True")
            
        return self.create_user(email,password, **extra_fields)
    
class User(AbstractBaseUser,PermissionsMixin):
    #Email is primary login  field 
    email = models.EmailField(unique=True)

    #phone is optional now will be used for OTP flows and mobile money receipts later
    phone = models.CharField(max_length=20, blank=True, null=True)

    #profile basics that drive eligibility and safety rules 
    display_name = models.CharField(max_length=20, blank=True)

    dob = models.DateField(blank=True,null=True)

    gender = models.CharField(max_length=20, blank=True)

    seeking = models.CharField(max_length=20, blank=True) 

    #verification flags that gate access to features
    email_verified = models.BooleanField(default=False)
    phone_verified= models.BooleanField(default=False)
    twofa_enabled = models.BooleanField(default=False)
    twofa_secret = models.CharField(max_length=64, blank=True, null=True)

    #Django admin and auth control flags 
    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now())


    #Email is the username field for authentication 
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email   


class Otpcode(models.Model):
    #stores short-lived OTP codes for phone or email purposes 
    target = models.CharField(max_length=255) # phone number or email 
    purpose = models.CharField(max_length=20) #  "phone-Login","phone_verify","unlock","email_verify"

    code = models.CharField(max_length=6)

    expires_at = models.DateTimeField()

    attempts = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def issue(cls, target: str,purpose: str, ttl_minutes: int = 5):
        code = f"{secrets.randbelow(1000000):06d}"
        obj = cls.objects.create(
              target=target,
              purpose=purpose,
              code=code,
              expires_at=timezone.now() + timedelta(minutes=ttl_minutes)
        )
        return obj
    
    def is_expired(self) -> bool:
        return timezone.now() >= self.is_expired_at
    


    class EmailVerifyToken(models.Model):
        #one-time token for email verification with expiry
        user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="email_tokens")
        token = models.CharField(max_length=64, unique=True)
        expire_at = models.DateTimeField()
        created_at = models.DateTimeField(auto_now_add=True)


        @classmethod
        def new_for(cls,user,ttl_hours:int = 24):
            token = secrets.token_urlsafe(32)
            return cls.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now()+ timedelta(hours=ttl_hours)
            )
        
        def is_expired(self) -> bool:
            return timezone.now() >= self.expire_at
