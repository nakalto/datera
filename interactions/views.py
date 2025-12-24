from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from .models import Swipe, Match, Like
from django.contrib.auth.decorators import login_required


def like_user(request, user_id):
    """
    Handle a 'like' action:
    -Get the target user
    -create or update a swipe user 
    -check for mutual like
    -if mutual, create a match and redirect to matches dashboard
    -if one-sided, redirect to accounts dashboard
    """
    # Get the user being liked
    to_user = get_object_or_404(User, id=user_id)

    
    # Try to get or create a Swipe record between current user and target
    swipe, created = Swipe.objects.get_or_create(
        from_user=request.user,      # current logged-in user
        to_user=to_user,             # target user being liked
        defaults={"is_like": True}   # if new, set is_like = True
    )

    #if the swipe already existed, update it to be a 'like'
    if not created:
        swipe.is_like = True
        swipe.save()

    #check if the target user arleady liked by the current user 
    if Swipe.objects.filter(from_user=to_user, to_user=request.user, is_like=True).exists():
        #Normalize ordering(smaller ID first) to prevent duplicate matches
        user1,user2 = sorted([request.user, to_user], key=lambda u:u.id) 
        #create the match if it doesn't arleady exist 
        Match.objects.get_or_create(user1=user1, user2=user2)
        #Redirect to matches dashboard if mutual like
        return redirect("interactions:matches_dashboard")
    
    #if only one-sided like, redirect back to accounts dashboard 
    return redirect("accounts:dashboard")
            


def dislike_user(request, user_id):
    """
    Handle a 'dislike' action:
    - Create a Swipe record (user dislikes another user)
    - No matching logic needed
    - Redirect to dashboard
    """

    # Get the user being disliked
    to_user = get_object_or_404(User, id=user_id)

    # Save the dislike action
    Swipe.objects.create(from_user=request.user, to_user=to_user, is_like=False)

    # Go back to the dashboard after disliking
    return redirect("accounts:dashboard")


@login_required
def matches_dashboard(request):
    """
    show all matches for the logged-in user.
    compute the partner(the other user) for each match.
    pass a list of dicts with partner info to the template.
    """
    #collect all matches for the logged-in user is either user1 or user2 
    matches = Match.objects.filter(user1=request.user)|Match.objects.filter(user2=request.user)

    #Order matches by newest first 
    matches = matches.order_by("-created_at")


    #build a list of dicts with partner info
    match_list = []
    for m in matches:
        partner = m.user2 if m.user1 == request.user else m.user1
        match_list.append({"match": m, "partner": partner})

    #Render the template with matches context 
    return render(request, "interactions/matches_dashboard.html", {"match_list": match_list})


@login_required
def likes_dashboard(request):
    """
    Show people who liked the logged-in user, but whom the user hasn't liked back yet.
    """

    # Query all Like objects where the current user is the target (i.e. people liked me)
    incoming_likes = Like.objects.filter(liked=request.user).select_related("liker")

    # Build a list of likes where I have NOT liked them back yet
    not_liked_back = [
        like for like in incoming_likes
        if not Like.objects.filter(liker=request.user, liked=like.liker).exists()
    ]

    # Render the likes_dashboard template with the filtered list
    return render(request, "interactions/likes_dashboard.html", {
        "likes": not_liked_back
    })


@login_required
def like_back(request, user_id):
    """
    Allow the logged-in user to like back someone who liked them.
    If mutual, create a Match and redirect to matches dashboard.
    """

    # Get the target user by ID (404 if not found)
    target = get_object_or_404(User, id=user_id)

    # Create a Like if it doesn't already exist
    Like.objects.get_or_create(liker=request.user, liked=target)

    # Check if target had already liked me (mutual like)
    if Like.objects.filter(liker=target, liked=request.user).exists():
        # If mutual, create a Match (only once)
        Match.objects.get_or_create(user1=request.user, user2=target)

    # Redirect to matches dashboard after liking back
    return redirect("interactions:matches_dashboard")