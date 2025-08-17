from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Otpcode, EmailVerifyToken
import pyotp

class RegisterSerializer(serializers.ModelSerializer):
    #Write-only password fields
    password = serializers.CharField(write_only=True,min_length=10)
    confirm_password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = ("email","password","confirm_password","display_name",)

        def validate(self,attrs):
            #checks if both password match 
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError({"confirm_password":"password do not match"})
            
            return attrs
        

        def create(self, validated_data):
            #Remove confirm_password before saving
            validated_data.pop("confirm_password")
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self,attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Email or password")
         
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")

        attrs["user"] = user

        return attrs 



class EmailVerifySendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        token = attrs["token"]

        try:
            user = User.objects.get(emails=attrs["email"])

        except User.DoesNotExist:
            raise serializers.ValidationError("No account with that email")    
        
        attrs["user"] = user

        return attrs


class EmailVerifyConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs["token"]

        try:
            evt = EmailVerifyToken.objects.select_related("user").get(token=token)

        except EmailVerifyToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or already usek token")
        
        
        if evt.is_expired():
            raise serializers.ValidationError("Token expired")
        
        attrs['evt'] = evt

        return attrs
    


class OtpSendSerializer(serializers.Serializer):
    phone = serializers.CharField() 

    def validate(self, attrs):
        phone = attrs["phone"]

        if not phone.startwith("+") and not phone[:2].isdigit():
            raise serializers.ValidationError("provide phone in international format" )
        
        attrs["phone"]  = phone
        return attrs


class OtpVerifySerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone = attrs["phone"]
        code = attrs["code"]

        try:
            otp = Otpcode.objects.filter(target=phone, purpose="phone_verify").latest("created_at")

        except Otpcode.DoesNotExist:
            raise serializers.ValidationError("No otp requested for this phone")


        if otp.is_expired():
              raise serializers.ValidationError("OTP expired")

        if otp.code != code:
            otp.attempts +=1
            otp.save(update_fields=["attempts"]) 
            raise serializers.ValidationError("OTP code is incorrect")

        attrs[otp] = otp
        return attrs    
            


class TwoFASetupStartSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance

class TwoFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        user:User = self.context["request"].user

        if not user.twofa_secret:
            raise serializers.ValidationError("2FA is not in set up state")

        totp = pyotp.TOTP(user.twofa_secret) 

        if not totp.verify(attrs["code"], valid_window=1):
            raise serializers.ValidationError("Invalid code")

        return attrs


class TwoFADisableSerializer(serializers.Serializer):
    confirm = serializers.BooleanField                      