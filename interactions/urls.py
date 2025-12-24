from django.urls import path 
from .import views

app_name = "interactions"

urlpatterns = [
    #Endpoint for liking a user
    path("like/<int:user_id>/", views.like_user, name="like_user"),
    # Endpoint for disliking a user
    path("dislike/<int:user_id>/", views.dislike_user, name="dislike_user"),
    path("matches/", views.matches_dashboard, name="matches_dashboard"),
    # Likes dashboard: shows people who liked the logged-in user
    path("likes/", views.likes_dashboard, name="likes_dashboard"),

    # Like-back action: when user likes back someone who liked them
    path("like-back/<int:user_id>/", views.like_back, name="like_back")
]