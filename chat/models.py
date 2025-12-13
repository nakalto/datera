from django.db import models
from django.utils import timezone
from accounts.models import User
from interactions.models import Match
# Create your models here.

class Message(models.Model):
    #Link each message to a Match
    match = models.ForeignKey(Match, on_delete=models.CASCADE,related_name="messages")

    #who sent the message
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")

    #message content
    content = models.TextField()

    #timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender}-> {self.match}"
    

    @property
    def receiver(self):
        """
        dynammicall compute the receiver:
        -if sender is user1, receiver is user2
        -if sender is user2 , receiver is user1
        """
        return self.match.user2 if self.sender == self.match.user1 else self.match.user1
    