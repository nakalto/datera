from rest_framework import serializers                  # serializer base classes and fields
from django.contrib.auth import authenticate            # used to verify email + password during login
from django.utils import timezone                       # provides timezone-aware "now" for expiry checks
import pyotp                                            # used for TOTP verification for 2FA

from .models import User, OtpCode, EmailVerifyToken     # our app models


class RegisterSerializer(serializers.ModelSerializer):
    # password is write_only so it never appears in responses
    # a minimum length is enforced at the API boundary
    password = serializers.CharField(write_only=True, min_length=10)
    # confirm_password is only used to check equality with password and is not saved to the database
    confirm_password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        # this serializer creates a User model instance
        model = User
        # confirm_password is included here for validation even though it is not a model field
        fields = ("email", "password", "confirm_password", "display_name", "phone", "dob", "gender", "seeking")

    def validate(self, attrs):
        # ensure password and confirm_password match to avoid typos at signup
        if attrs["password"] != attrs["confirm_password"]:
            # raise a field-specific error so the frontend can highlight that input
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        # remove confirm_password since it does not exist on the User model
        validated_data.pop("confirm_password")
        # extract the raw password so we can hash it via set_password
        raw_password = validated_data.pop("password")
        # build a user instance with the remaining validated fields
        user = User(**validated_data)
        # hash and store the password securely
        user.set_password(raw_password)
        # persist the user to the database
        user.save()
        # return the created user to the view
        return user


class LoginSerializer(serializers.Serializer):
    # the client submits email and password to log in
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # authenticate against Django's auth backend using email as the username field
        user = authenticate(username=attrs["email"], password=attrs["password"])
        if not user:
            # return a clear error when credentials are wrong
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            # block disabled or banned accounts
            raise serializers.ValidationError("Account is disabled")
        # attach the user object so the view can log them in after validation
        attrs["user"] = user
        return attrs


class EmailVerifySendSerializer(serializers.Serializer):
    # the client provides an email to re-send a verification link
    email = serializers.EmailField()

    def validate(self, attrs):
        # fetch the user for that email or fail fast if none exists
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("No account with that email")
        # stash the user for the view to avoid a second database lookup
        attrs["user"] = user
        return attrs


class EmailVerifyConfirmSerializer(serializers.Serializer):
    # the client provides the token from the verification link
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs["token"]
        # try to load the token and the associated user in one query
        try:
            evt = EmailVerifyToken.objects.select_related("user").get(token=token)
        except EmailVerifyToken.DoesNotExist:
            # invalid token or one that was already consumed
            raise serializers.ValidationError("Invalid or already used token")
        # check token expiry using a timezone-aware comparison
        if timezone.now() >= evt.expires_at:
            raise serializers.ValidationError("Token expired")
        # pass the token row to the view so it can mark the user verified and delete the token
        attrs["evt"] = evt
        return attrs


class OtpSendSerializer(serializers.Serializer):
    # the client submits a phone number to receive an OTP
    phone = serializers.CharField()

    def validate(self, attrs):
        phone = attrs["phone"]
        # a simple sanity check; a library like "phonenumbers" can replace this later for strict validation
        if not phone or len(phone) < 6:
            raise serializers.ValidationError("Provide a valid phone number")
        # store back the phone so the view has a normalized value
        attrs["phone"] = phone
        return attrs


class OtpVerifySerializer(serializers.Serializer):
    # the client submits the phone number and the 6-digit OTP they received
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone = attrs["phone"]
        code = attrs["code"]
        # fetch the most recent OTP for this phone and the specific purpose
        try:
            otp = OtpCode.objects.filter(target=phone, purpose="phone_verify").latest("created_at")
        except OtpCode.DoesNotExist:
            # if the user never requested an OTP, tell them to request one first
            raise serializers.ValidationError("No OTP requested for this phone")
        # reject expired OTPs
        if otp.is_expired():
            raise serializers.ValidationError("OTP expired")
        # reject incorrect codes and count the failed attempt
        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            raise serializers.ValidationError("OTP code is incorrect")
        # attach the OTP row so the view can mark the phone verified and delete the OTP
        attrs["otp"] = otp
        return attrs


