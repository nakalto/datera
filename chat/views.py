# Import decorators and shortcuts
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Import models
from interactions.models import Match
from .models import Message
# Create your views here.

@login_required
def chat_view(request, match_id):
    """
    display chat message for a given match and allow sending new ones 

    """

    #Get the match object by ID (404 if not found)
    match = get_object_or_404(Match, id=match_id)
    
    #ensure login user is part of this match 
    if request.user not in [match.user1, match.user2]:
        return redirect("interactions:matches_dashboard")
    

    #handle new message submission 
    if request.method == "POST":
        #Get the message content from the form 
        content = request.POST.get("content")
        #if content is not empy, create new message record
        if content:
            Message.objects.create(match=match, sender=request.user, content=content)
        #Ridirect back to the same chatview(prevents resubmission on refresh )    
        return redirect("chat:chat_view", match_id=match_id)
    
    #Get all messages for this match, ordered by creation time
    messages = match.messages.order_by("created_at")

    #compute the partner (the other user in the match)
    partner = match.user2 if match.user1 == request.user else match.user1

    #Render the chart template with match, partner and messages 
    return render(request, "chat/chat.html", {
        "match":match,
        "partner": partner,
        "messages":messages,
    })