# Import decorators and shortcuts
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Import models
from interactions.models import Match
from .models import Message

@login_required
def chat_view(request, match_id):
    """
    Display chat messages for a given match and allow sending new ones.
    """

    # Get the match object by ID (404 if not found)
    match = get_object_or_404(Match, id=match_id)
    
    # Ensure logged-in user is part of this match
    if request.user not in [match.user1, match.user2]:
        return redirect("interactions:matches_dashboard")
    
    # Handle new message submission
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(match=match, sender=request.user, content=content)
        # Redirect back to the same chat view (prevents resubmission on refresh)
        return redirect("chat:chat_view", match_id=match_id)
    
    # Get all messages for this match, ordered by creation time
    messages = match.messages.order_by("created_at")

    # Compute the partner (the other user in the match)
    partner_user = match.user2 if match.user1 == request.user else match.user1
    partner_profile = partner_user.profile  # ✅ get the Profile object

    # Render the chat template with match, partner profile, and messages
    return render(request, "chat/chat.html", {
        "match": match,
        "partner": partner_profile,
        "messages": messages,
    })
