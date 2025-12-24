# Import path function for defining URL routes
from django.urls import path

# Import views from the accounts app
from . import views

# Define namespace for this app's URLs (helps avoid conflicts with other apps)
app_name = 'accounts'

# Define URL patterns for the accounts app
urlpatterns = [
    # Route for login page → calls start_login view
    path('login/', views.start_login, name='start_login'),

    # Route for OTP verification page → calls verify view
    path('verify/', views.verify, name='verify'),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("explore/", views.explore, name="explore"),

    path("profile/", views.profile, name="profile"),

    path("profile/<int:user_id>/", views.profile_view, name="profile_view"), 
]
