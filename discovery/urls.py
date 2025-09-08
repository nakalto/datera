from django.urls import path
from .views import DiscoverView
urlpatterns = [ path("cards/", DiscoverView.as_view(), name="discover-cards") ]
