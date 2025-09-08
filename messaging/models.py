from django.db import models
from django.conf import settings

class Thread(models.Model):
    a = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="threads_a",on_delete=models.CASCADE)
    b = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="thread_b",on_delete=models.CASCADE)
    a_first_free_used = models.BooleanField(default=False)
    b_first_free_used = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["a","b"], name="unique_pair")]


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)        