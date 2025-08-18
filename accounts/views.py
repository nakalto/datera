from django.shortcuts import render
from django.contrib.auth import login,logout
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django .conf import settings
from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
import pyotp

from .serializers import(
    RegisterSerializer,LoginSerializer,EmailVerifyConfirmSerializer,
    EmailVerifySendSerializer,OtpSendSerializer,OtpVerifySerializer,
    TwoFASetupStartSerializer,TwoFAVerifySerializer,TwoFADisableSerializer
)

from .models import User,Otpcode, EmailVerifyToken




class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    #register a new user and return a minimal profile payload 
    def post(self,request):
        serialiarizers = RegisterSerializer(data=request.data)
        if not serialiarizers.is_valid():
            return Response(serialiarizers.errors, status=status.HTTP_400_BAD_REQUEST)


        #save user  
        user = serialiarizers.save() 

        #create email verification token 
        evt = EmailVerifyToken.new_for(user)
        verify_link = f"{request.build_absolute_uri('/auth/verify-email')}?token={evt.token}"   

        send_mail(
            subject="verify your Datera Email",
            message=f"click link to verify: {verify_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        #return a success message with the email 
        return Response({"message":"registration sucessful. please check your email ","email":user.email })
    





class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    #Authenticates via email + password and start session 
    def post(self,request):
        serialiarizers = LoginSerializer(data = request.data)
        if not serialiarizers.is_valid():
            return Response(serialiarizers.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serialiarizers.validated_data["user"]

        #Enforce email verification before login desired
        if not user.email_verified:
            return Response({"detail":"please verify your email first."}, status=403)

        #Csrf-protected session login; session id is rotated autoamatically
        login(request,user)
        csrf = get_token(request)

        if user.twofa_enabled:
           #Mark session as pending 2FA; frontend should redirect to /auth/2fa/
           request.session["twofa_pending"] = user.id
           
           return Response("message","login successful")
          
            
        

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    #end the current session for authenticated user 
    def post(self,request):
        logout(request)
        return Response({"message":"logout successfull"},status=status.HTTP_200_OK)
       
        
    


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
                                                      
    #return current authenticated user's profile 
    def get(self,request):
        user:User = request.user

        return Response(
            {
                "email":user.email,
                "display_name": user.display_name,
                "phone":user.phone,
                "email_verified":user.email_verified,
                "phone_verified":user.phone_verified,
                "twofa_enabled":user.twofa_enabled,
            }
        )
    

class EmailVerifySendView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        s = EmailVerifySendSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors,status=400)
        
        user = s.validated_data["user"]

        evt = EmailVerifyToken.new_for(user)

        link = f"{request.build_absolute_uri('/auth/verify-email/')}?token={evt.token}"

        send_mail(
            subject="Verify your datera email",
            link= f"click link to verify: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({"message": "Verification email sent"}, status=200)


class EmailVerifyConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        s = EmailVerifyConfirmSerializer(data=request.data)

        if not s.is_valid():
            return Response(s.errors,status=400)
        

        evt: EmailVerifyToken = s.validated_data["evt"]

        user = evt.user

        if evt.is_expired():
            return Response({"detail": "token expired"})
        
        user.email_verified = True

        user.save(update_fields = ["email_verified"])

        evt.delete()

        return Response({"message": "Email verified"}, status=200)
    


class PhoneOtpSendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = OtpSendSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        
        phone = s.validated_data["phone"]

        otp = Otpcode.issue(target=phone, purpose="phone_verify",ttl_minutes=5)

        # TODO integrate SMS gateway (M-Pesa/Tigo/Airtel aggregator or Africa's Talking)
        # For now we log/send via email as placeholder

        send_mail(
            subject="Your Datera phone OTP",
            message=f"OTP: {otp.code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True,
        )
        return Response({"message": "OTP sent"}, status=200)
    
class  PhoneOtpVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def post(self,request):
        s = OtpVerifySerializer(data = request.data)

        if not s.is_valid():
            return Response(s.errors,status=400)
        
        otp: Otpcode = s.validated_data["otp"]

        #Mark phone verified on the current user and store phone if not set
        u: User =  request.user

        if not u.phone:
            u.phone  = otp.target

        u.phone_verified = True

        u.save(update_fields=["phone", "phone_verified"])

        otp.delete()

        return Response({"message":"phone verified"}, status=200)    



