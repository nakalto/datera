import random
from datetime import timedelta
from django.utils import timezone
from .models import OTP

def create_otp(user, purpose='login')
    code = f"{random.randint(100000,999999)}"
    expires = timezone.now() + timedelta(minutes=5)
    return OTP.objects.create(user=user, code=code, purpose=purpose, expire_at=expires )
