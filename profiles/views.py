from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from .serializers import ProfileSerializer

class MeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = Profile.objects.get(user=request.user)
        return Response({
            "display_name": p.display_name,
            "bio": p.bio,
            "gender":p.gender,
            "seeking":p.seeking,
            "dob":p.dob,
            "location":p.location,
            "is_visible":p.is_visible,

        })
    

class ProfileMeUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    def get_object(self):
        return Profile.objects.get(user=self.request.user)

