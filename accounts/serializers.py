from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

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

