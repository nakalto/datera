from django.shortcuts import render, redirect,get_object_or_404

# Import get_user_model (to fetch custom User model) and login (to log user into session)
from django.contrib.auth import get_user_model, login
from django.contrib import messages

# Restrict views to certain HTTP methods (GET and POST only)
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .otp import create_otp
from accounts.models import User
from profiles.models import Profile  # import your Profile model
from .models import OTP
from django.core.paginator import Paginator
from django.contrib.auth import logout

# Import phone utilities (normalize and validate Tanzanian numbers)
from .phone import normalize_msisdn, is_valid_tz
# Import SMS sending function
from .sms import send_sms
# Get the custom User model defined in accounts/models.py
User = get_user_model()
# Restrict this view to GET and POST requests
@require_http_methods(["GET", "POST"])
def start_login(request):
    # If the request is a POST (form submitted)
    if request.method == "POST":
        # Get raw phone number from form input
        raw = request.POST.get("phone")

        # Normalize phone number to E.164 format (+255...)
        phone = normalize_msisdn(raw)

        # Validate Tanzanian phone number format
        if not is_valid_tz(phone):
            # Show error message if invalid
            messages.error(request, "Enter a valid phone number (e.g., +255712345678)")
            # Re-render login form
            return render(request, 'accounts/start_login.html')
        
        # Get existing user or create new one with this phone
        user, _ = User.objects.get_or_create(phone=phone, defaults={'username': phone})

        # Generate OTP for this user
        otp = create_otp(user, 'phone_login')

        # Send OTP via SMS (mock in dev, Africa's Talking in prod)
        send_sms(phone, f"Datera code: {otp.code}. Expires in 5 minutes.")

        # Save user ID in session for verification step
        request.session['pending_user_id'] = user.id

        # Redirect to verify page
        return redirect('accounts:verify')

    # If request is GET, show login form
    return render(request, 'accounts/start_login.html')


# Restrict this view to GET and POST requests
@require_http_methods(["GET", "POST"])
def verify(request):
    """
    Handles OTP verification:
    - GET → show OTP form
    - POST → check OTP validity
    - If valid → log user in, then redirect:
        * Dashboard if onboarding_complete=True
        * Onboarding flow if onboarding_complete=False
    """

    # 1. Get pending user ID from session
    uid = request.session.get('pending_user_id')
    if not uid:
        return redirect('accounts:start_login')

    # 2. Fetch user from database
    user = User.objects.get(id=uid)

    # Ensure the user has a Profile
    profile, created = Profile.objects.get_or_create(user=user)

    # 3. Handle POST (form submitted)
    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        otp = OTP.objects.filter(user=user, purpose='phone_login').order_by('-created_at').first()

        if not otp:
            messages.error(request, 'No code found. Please request a new one.')
            return render(request, 'accounts/verify.html', {'user': user})

        otp.attempts += 1
        otp.save(update_fields=['attempts'])

        if otp.is_valid() and otp.code == code:
            otp.consumed = True
            otp.save(update_fields=['consumed'])

            user.phone_verified = True
            user.save(update_fields=['phone_verified'])

            login(request, user)
            messages.success(request, 'Logged in successfully.')

            # ✅ Redirect based on onboarding status
            if profile.onboarding_complete:
                return redirect('profiles:dashboard')
            else:
                return redirect('profiles:onboarding_name')

        messages.error(request, 'Invalid or expired code.')
        return render(request, 'accounts/verify.html', {'user': user})

    # 4. Handle GET → show OTP form
    return render(request, 'accounts/verify.html', {'user': user})

                                  

def logout_view(request):
    logout(request)
    return redirect('accounts:start_login')
