from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    EmailVerifySendView, EmailVerifyConfirmView,
    PhoneOtpSendView, PhoneOtpVerifyView,
    TwoFASetupStartView, TwoFAVerifyView, TwoFADisableView, TwoFALoginVerifyView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/",    LoginView.as_view(),    name="auth-login"),
    path("logout/",   LogoutView.as_view(),   name="auth-logout"),
    path("me/",       MeView.as_view(),       name="auth-me"),

    path("email/send-verify/", EmailVerifySendView.as_view(),   name="email-send-verify"),
    path("email/confirm/",     EmailVerifyConfirmView.as_view(), name="email-confirm"),

    path("phone/otp/send/",   PhoneOtpSendView.as_view(),   name="phone-otp-send"),
    path("phone/otp/verify/", PhoneOtpVerifyView.as_view(), name="phone-otp-verify"),

    path("2fa/setup/",         TwoFASetupStartView.as_view(),  name="2fa-setup"),
    path("2fa/verify/",        TwoFAVerifyView.as_view(),      name="2fa-verify"),
    path("2fa/disable/",       TwoFADisableView.as_view(),     name="2fa-disable"),
    path("2fa/login-verify/",  TwoFALoginVerifyView.as_view(), name="2fa-login-verify"),
]
