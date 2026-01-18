# Import Django's path function for defining URL routes
from django.urls import path

# Import the views we created in interactions/views.py
from . import views

app_name = "interactions"

# Define the URL patterns for the interactions app
urlpatterns = [
    # Route for liking a user
    # Example: /interactions/like/5/ → likes user with ID=5
    path("like/<int:user_id>/", views.like_user, name="like_user"),

    # Route for disliking a user
    # Example: /interactions/dislike/5/ → dislikes user with ID=5
    path("dislike/<int:user_id>/", views.dislike_user, name="dislike_user"),

    # Route for viewing all matches for the logged-in user
    # Example: /interactions/matches/ → shows matches dashboard
    path("matches/", views.matches_dashboard, name="matches_dashboard"),

    path("likes/", views.likes_dashboard, name="likes_dashboard"),


]
