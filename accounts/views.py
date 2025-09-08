from django.contrib.auth import login, logout  # session management helpers
from django.middleware.csrf import get_token   # used to return CSRF token to frontend after login
from django.core.mail import send_mail         # used to send email verification links and temporary OTPs
from django.conf import settings               # holds email settings and other configuration
from rest_framework.views import APIView       # base class for simple DRF views
from rest_framework.response import Response   # standard JSON response object
from rest_framework import status, permissions # HTTP codes and permission classes
import pyotp                                   # library for TOTP-based two factor authentication

# we import serializers that validate input and format output
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    EmailVerifySendSerializer,
    EmailVerifyConfirmSerializer,
    OtpSendSerializer,
    OtpVerifySerializer,
    
)

# we import models used by the logic in these views
from .models import User, OtpCode, EmailVerifyToken


class RegisterView(APIView):
    """
    Handles creating a new user account.
    Accepts JSON with email, password, and optional profile fields.
    On success, creates an email verification token and sends a verification email.
    """
    permission_classes = [permissions.AllowAny]  # anyone can hit registration

    def post(self, request):
        # validate incoming data against RegisterSerializer rules
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            # return validation errors to the client if something is wrong
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # create the user using the serializer's create method
        user = serializer.save()

        # create a one-time email verification token for this user
        evt = EmailVerifyToken.new_for(user)

        # build an absolute verification link that points to your verify page
        # the page's JS will POST the token to /api/auth/email/confirm/
        verify_link = f"{request.build_absolute_uri('/auth/verify-email/')}?token={evt.token}"

        # send an email with the verification link
        # fail_silently=True means we won't crash if email fails during local dev
        send_mail(
            subject="Verify your Datera email",
            message=f"Click this link to verify your email: {verify_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        # return a success message so the frontend can navigate the user appropriately
        return Response({"message": "Registration successful. Please check your email to verify."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Handles email + password login.
    If the account is not email verified, login is blocked.
    If 2FA is enabled, marks the session as pending 2FA and asks the client to complete TOTP.
    """
    permission_classes = [permissions.AllowAny]  # anyone can attempt to log in

    def post(self, request):
        # validate credentials
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer attaches the authenticated user to validated_data if credentials are correct
        user: User = serializer.validated_data["user"]

        # require email verification before allowing a full login
        if not user.email_verified:
            return Response({"detail": "Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)

        # start a session for this user
        login(request, user)

        # return a CSRF token to the frontend so it can make subsequent POSTs safely
        csrf = get_token(request)

        # if the user has 2FA enabled, we require a second step before granting full access
        if user.twofa_enabled:
            # we set a temporary session flag to remember that 2FA is pending for this user
            request.session["twofa_pending"] = user.id
            # we return a payload that tells the frontend to redirect to the 2FA verification screen
            return Response({"message": "2FA required", "twofa": True, "csrfToken": csrf}, status=status.HTTP_200_OK)

        # if no 2FA is needed, login is complete
        return Response({"message": "Login successful", "csrfToken": csrf}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logs the current user out by clearing their session.
    """
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users can log out

    def post(self, request):
        # end the session for this user
        logout(request)
        # acknowledge success
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    Returns a small snapshot of the authenticated user's account state.
    Useful for populating UI state after page load.
    """
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users can see their profile snapshot

    def get(self, request):
        # request.user is the authenticated user object
        u: User = request.user
        # we return only safe, essential fields
        payload = {
            "email": u.email,
            "display_name": u.display_name,
            "phone": u.phone,
            "email_verified": u.email_verified,
            "phone_verified": u.phone_verified,
            "twofa_enabled": u.twofa_enabled,
        }
        return Response(payload, status=status.HTTP_200_OK)


class EmailVerifySendView(APIView):
    """
    Generates and emails a fresh verification token for an existing account.
    """
    permission_classes = [permissions.AllowAny]  # we allow anyone to request a verify email by email address

    def post(self, request):
        # validate the provided email and fetch the user
        s = EmailVerifySendSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer guarantees a valid user in validated_data
        user: User = s.validated_data["user"]

        # create a new token for the user
        evt = EmailVerifyToken.new_for(user)

        # construct the verification link that the user can click
        link = f"{request.build_absolute_uri('/auth/verify-email/')}?token={evt.token}"

        # send the email with the link
        send_mail(
            subject="Verify your Datera email",
            message=f"Click this link to verify your email: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        # let the client know the email was sent
        return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)


class EmailVerifyConfirmView(APIView):
    """
    Confirms an email verification token.
    Sets email_verified to True and removes the token.
    """
    permission_classes = [permissions.AllowAny]  # token-based, no auth required

    def post(self, request):
        # validate the token payload
        s = EmailVerifyConfirmSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer attaches the token record for us
        evt: EmailVerifyToken = s.validated_data["evt"]
        user = evt.user

        # mark the user as email verified
        user.email_verified = True
        user.save(update_fields=["email_verified"])

        # delete the token so it cannot be reused
        evt.delete()

        # confirm success
        return Response({"message": "Email verified"}, status=status.HTTP_200_OK)


class PhoneOtpSendView(APIView):
    """
    Issues a 6-digit OTP to verify the user's phone number.
    This endpoint expects the user to be logged in.
    In production you would integrate an SMS gateway to deliver the OTP.
    """
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users can verify their phone

    def post(self, request):
        # validate the provided phone number format
        s = OtpSendSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        # get the normalized phone from the serializer
        phone = s.validated_data["phone"]

        # issue a new OTP that expires in 5 minutes by default
        otp = OtpCode.issue(target=phone, purpose="phone_verify", ttl_minutes=5)

        # send the code; for now we send via email to the user's email as a placeholder
        # replace this with an SMS provider integration when ready
        send_mail(
            subject="Your Datera phone OTP",
            message=f"Your verification code is: {otp.code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True,
        )

        # acknowledge that the OTP was sent
        return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


class PhoneOtpVerifyView(APIView):
    """
    Verifies the OTP code for the phone number.
    On success, marks the phone as verified and optionally stores the phone if not present.
    """
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users can finish phone verification

    def post(self, request):
        # validate phone and code
        s = OtpVerifySerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        # the serializer returns the matching OtpCode object
        otp: OtpCode = s.validated_data["otp"]

        # mark the user's phone as verified and save the number if it was not saved before
        u: User = request.user
        if not u.phone:
            u.phone = otp.target
        u.phone_verified = True
        u.save(update_fields=["phone", "phone_verified"])

        # remove the OTP record so it cannot be reused
        otp.delete()

        # confirm success
        return Response({"message": "Phone verified"}, status=status.HTTP_200_OK)

