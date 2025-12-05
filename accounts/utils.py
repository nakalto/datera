# Import Python's random module to generate random numbers
import random

# Import timedelta to calculate expiry time duration
from datetime import timedelta

# Import timezone utilities from Django to get current time safely
from django.utils import timezone

# Import the OTP model we defined earlier
from .models import OTP


# Define function to create a new OTP
# Parameters:
# - user: the User object linked to this OTP
# - purpose: reason for OTP (default is 'login')
def create_otp(user, purpose='login'):

    # Generate a random 6-digit code between 100000 and 999999
    code = f"{random.randint(100000, 999999)}"

    # Set expiry time to 5 minutes from now
    expires = timezone.now() + timedelta(minutes=5)

    # Create and save OTP object in database with user, code, purpose, and expiry
    return OTP.objects.create(user=user, code=code, purpose=purpose, expires_at=expires)
