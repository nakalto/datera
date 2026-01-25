# Import Django shortcuts for rendering templates, redirecting, and safely fetching objects
from django.shortcuts import render, redirect, get_object_or_404

# Import the active User model from accounts app (custom user model)
from accounts.models import User

# Import our interaction models (Swipe and Match)
from .models import Swipe, Match

# Import decorator to ensure only logged-in users can access these views
from django.contrib.auth.decorators import login_required



# Handle a "like" action (swipe right)

@login_required
def like_user(request, user_id):
    """
    Handle a 'like' action:
    - Get the target user
    - Create or update a Swipe record
    - Check for mutual like
    - If mutual, create a Match and redirect to matches dashboard
    - If one-sided, redirect back to dashboard
    """

    # Step 1: Get the user being liked (404 if not found)
    to_user = get_object_or_404(User, id=user_id)

    # Step 2: Create or update a Swipe record (ensures no duplicates)
    # If a swipe already exists, update it to is_like=True
    swipe, created = Swipe.objects.update_or_create(
        from_user=request.user,      # current logged-in user
        to_user=to_user,             # target user being liked
        defaults={"is_like": True}   # set is_like = True
    )

    # Step 3: Check if the target user already liked the current user
    if Swipe.objects.filter(from_user=to_user, to_user=request.user, is_like=True).exists():
        # Normalize ordering (smaller ID first) to prevent duplicate matches
        user1, user2 = sorted([request.user, to_user], key=lambda u: u.id)

        # Step 4: Create the match if it doesn't already exist
        Match.objects.get_or_create(user1=user1, user2=user2)

        # Step 5: Redirect to matches dashboard if mutual like
        return redirect("interactions:matches_dashboard")

    # Step 6: If only one-sided like, redirect back to dashboard
    return redirect("profiles:dashboard")



# Handle a "dislike" action (swipe left)
@login_required
def dislike_user(request, user_id):
    """
    Handle a 'dislike' action:
    - Get the target user
    - Create or update a Swipe record (user dislikes another user)
    - No matching logic needed
    - Redirect to dashboard
    """

    # Step 1: Get the user being disliked (404 if not found)
    to_user = get_object_or_404(User, id=user_id)

    # Step 2: Save the dislike action (update if already exists)
    Swipe.objects.update_or_create(
        from_user=request.user,      # current logged-in user
        to_user=to_user,             # target user being disliked
        defaults={"is_like": False}  # set is_like = False
    )

    # Step 3: Go back to the dashboard after disliking
    return redirect("profiles:dashboard")



# Show all matches for the logged-in user
@login_required
def matches_dashboard(request):
    """
    Show all matches for the logged-in user:
    - Collect matches where user is either user1 or user2
    - Order matches by newest first
    - Build a list of dicts with partner profile info
    - Render the template with matches context
    """

    # Step 1: Collect all matches where the logged-in user is either user1 or user2
    matches = Match.objects.filter(user1=request.user) | Match.objects.filter(user2=request.user)

    # Step 2: Order matches by newest first
    matches = matches.order_by("-created_at")

    # Step 3: Build a list of dicts with partner info
    match_list = []
    for m in matches:
        # Determine the partner (the other user in the match)
        partner_user = m.user2 if m.user1 == request.user else m.user1
        partner_profile = partner_user.profile  # get Profile object

        # Append match and partner info to list
        match_list.append({"match": m, "partner": partner_profile})

    # Step 4: Render the template with matches context
    return render(request, "interactions/matches_dashboard.html", {"match_list": match_list})


# Show incoming likes (people who liked me but I haven't liked back yet)
@login_required
def likes_dashboard(request):
    """
    Show people who liked the logged-in user, but whom the user hasn't liked back yet:
    - Get all swipes where someone liked me
    - Filter out cases where I already liked them back
    - Render the template with the filtered list
    """

    # Step 1: Get all swipes where someone liked me
    incoming_likes = Swipe.objects.filter(
        to_user=request.user,     # I am the target user
        is_like=True,             # only likes, not dislikes
    ).select_related("from_user")  # optimize query by fetching liker info

    # Step 2: Filter out cases where I already liked them back
    not_liked_back = [
        swipe for swipe in incoming_likes
        if not Swipe.objects.filter(
            from_user=request.user,    # me liking them
            to_user=swipe.from_user,   # the person who likes me
            is_like=True               # must be a like
        ).exists()
    ]

    # Step 3: Render template with the filtered list
    return render(request, "interactions/likes_dashboard.html", {"likes": not_liked_back})
