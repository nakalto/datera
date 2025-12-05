from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .otp import create_otp
from .models import OTP
from .phone import normalize_msisdn, is_valid_tz

User = get_user_model()
@require_http_methods(["GET", "POST"])
def start_login(request):
    if request.method == "POST":
        raw = request.POST.get("phone")
        phone = normalize_msisdn(raw)
        if not is_valid_tz(phone):
            messages.error(request, "enter a valid phone number (e.g., +255712345678)")
            return render(request, 'accounts/start_login.html')
        
        user, _ = User.objects.get_or_create(phone=phone, defaults={'username':phone})
        otp = create_otp(user, 'phone_login')
        send_sms(phone, f"Datera code: {otp.code}. Expires in 5 minutes.")
        request.session['pending_user_id'] = user.id
        return redirect('accounts:verify')
    return render(request, 'accounts/start_login.html')


@require_http_methods(["GET", "POST"])
def verify(request):
    uid = request.session.get('pending_user_id')
    if not uid:
        return redirect('accounts:start_login')
    user = User.objects.get(id=uid)
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        otp = OTP.objects.filter(user=user, purpose='phone_login').order_by('-created_at').first()

        if not otp:
            messages.error(request, 'No code found. please request a new one.')
            return render(request, 'accounts/verify.html')
        otp.attempts += 1
        otp.save(update_fields=['attempts'])

        if otp.is_valid() and otp.code == code:
            otp.consumed = True
            otp.save(update_fields=['consumed'])
            user.phone_verified = True
            user.save(update_fields=['phone_verified'])
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('profiles:onboarding')
        messages.error(request, 'Invalid or expired code.')
        return render(request, 'accounts/verify.html', {'user':user})
        



