from django.db import models
from django.conf import settings
from django.utils import timezone

class Match(models.Model):
    #Mutual match models
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='matches_initiated',
        on_delete=models.CASCADE
    )

    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='matches_received',
        on_delete=models.CASCADE        
    )

    created_at = models.DateTimeField(auto_now_add=True)
      
    #prevent duplicate matches   
    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Match: {self.user1.username} ❤️ {self.user2.username}"    
    

class Swipe(models.Model):
    #user who perfoms the swipe(like or dislike)
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   #reference to user model
        related_name="swipes_sent",  # Reverse lookup: user swipes_received all()
        on_delete=models.CASCADE  #Delete swipe if user delete 
    )  

    #User who was swipes on
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="swipe_received",
        on_delete=models.CASCADE
    ) 

    #Boolean fields: True = like, False = dislike
    is_like = models.BooleanField(default=False)

    #Timestamp when the swipe happened 
    created_at = models.DateTimeField(auto_now_add=True)

    #optional reaction field for advanced emoj and tag
    reaction = models.CharField(max_length=16, blank=True)


    #Meta options for swipe models
    class Meta:
        #Ensure a user can only swipe another user once 
        unique_together = ("from_user", "to_user")

    #override the save method to add custom logic 
    def save(self, *args, **kwargs):
        #call the original save method to store swipe 
        super().save(*args, **kwargs)

        #Only check for matches if this swipe is a like  
        if self.is_like:
            #Look for a reciprocal like from the other user 
            reciprocal = Swipe.objects.filter(
                from_user=self.to_user,
                to_user=self.from_user,
                is_like=True

            ).exists()

            #if reciprocal like exists, create match automatically 
            if reciprocal:
                #Normalize ordering(smaller id first) to prevent duplicate matches     
                user1, user2 = sorted([self.from_user, self.to_user], key=lambda u: u.id)
                Match.objects.get_or_create(user1=user1, user2=user2)


    #string representation for debugging/admin
    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({'Like' if self.is_like else 'Dislike' })"     