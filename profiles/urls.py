from django.urls import path
from .views import MeProfileView

urlpatterns = [
    path("me/", MeProfileView.as_view(), name="me-profile"),
    path("me/", MeProfileView.as_view(), name="profile-me"),

]
