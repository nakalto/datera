# Import render (to display templates) and redirect (to navigate to another view)
from django.shortcuts import render, redirect

# Import get_user_model (to fetch custom User model) and login (to log user into session)
from django.contrib.auth import get_user_model, login

# Import Django messages framework (for success/error feedback to user)
from django.contrib import messages

# Restrict views to certain HTTP methods (GET and POST only)
from django.views.decorators.http import require_http_methods

# Import our OTP generator function
from .otp import create_otp

# Import OTP model
from .models import OTP

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
    # Get pending user ID from session
    uid = request.session.get('pending_user_id')

    # If no user ID in session, redirect back to login
    if not uid:
        return redirect('accounts:start_login')

    # Fetch user from database
    user = User.objects.get(id=uid)

    # If the request is a POST (form submitted)
    if request.method == "POST":
        # Get OTP code from form input, strip spaces
        code = request.POST.get("code", "").strip()

        # Find latest OTP for this user with purpose 'phone_login'
        otp = OTP.objects.filter(user=user, purpose='phone_login').order_by('-created_at').first()

        # If no OTP found, show error and re-render verify form
        if not otp:
            messages.error(request, 'No code found. Please request a new one.')
            return render(request, 'accounts/verify.html')

        # Increment attempts counter
        otp.attempts += 1
        # Save updated attempts count
        otp.save(update_fields=['attempts'])

        # If OTP is valid and code matches
        if otp.is_valid() and otp.code == code:
            # Mark OTP as consumed
            otp.consumed = True
            otp.save(update_fields=['consumed'])

            # Mark user's phone as verified
            user.phone_verified = True
            user.save(update_fields=['phone_verified'])

            # Log user into Django session
            login(request, user)

            # Show success message
            messages.success(request, 'Logged in successfully.')

            # Redirect to profile onboarding
            return redirect('profiles:onboarding')

        # If OTP invalid or expired, show error
        messages.error(request, 'Invalid or expired code.')

        # Re-render verify form with user context
        return render(request, 'accounts/verify.html', {'user': user})
