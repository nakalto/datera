import random
# Import timedelta to calculate expiry duration
from datetime import timedelta
# Import timezone utilities from Django to get current time safely
from django.utils import timezone
# Import the OTP model (defined in models.py)
from .models import OTP

# Function to create a new OTP for a user
def create_otp(user, purpose='login'):
    # Generate a random 6-digit code between 100000 and 999999
    code = f"{random.randint(100000, 999999)}"

    # Set expiry time to 5 minutes from now
    expires = timezone.now() + timedelta(minutes=5)

    # Create and save OTP object in database with user, code, purpose, and expiry
    return OTP.objects.create(
        user=user,          # link OTP to user
        code=code,          # store generated code
        purpose=purpose,    # store purpose (default 'login')
        expires_at=expires  # store expiry timestamp
    )
