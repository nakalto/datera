from django.shortcuts import render
from django.contrib.auth import login,logout
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .serializers import RegisterSerializer, LoginSerializer
from .models import User




class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    #register a new user and return a minimal profile payload 
    def post(self,request):
        serialiarizers = RegisterSerializer(data=request.data)
        if not serialiarizers.is_valid():
            return Response(serialiarizers.errors, status=status.HTTP_400_BAD_REQUEST)


        #save user  
        user = serialiarizers.save()    

        #return a success message with the email 
        return Response({"message":"registration sucessful. please verify your email to continue.","email":user.email })
    





class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    #Authenticates via email + password and start session 
    def post(self,request):
        serialiarizers = LoginSerializer(data = request.data)
        if not serialiarizers.is_valid():
            return Response(serialiarizers.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serialiarizers.validated_data["user"]

        #Csrf-protected session login; session id is rotated autoamatically
        login(request,user)
        csrf = get_token(request)
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

        payload = {
            "email":user.email,
            "display_name":user.display_name,
            "phone":user.phone,
            "email_verified":user.email_verified,
            "phone_verified":user.phone_verified,

        }
        return Response(payload,status=status.HTTP_200_OK)