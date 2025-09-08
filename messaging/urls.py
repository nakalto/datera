from django.urls import path
from .views import SendMessageView
urlpatterns = [ 
    path("send/<int:user_id>/", SendMessageView.as_view(), name="chat-send") 
    ]
