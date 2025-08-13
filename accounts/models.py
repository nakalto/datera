from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    #Create a regular user with emails as the unique identifier
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
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
