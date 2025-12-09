from django.urls import path
from .import views

urlpatterns = [
    path('onboarding/name/', views.onboarding_name, name='onboarding_name'),
    path('onboarding/gender/', views.onboarding_gender, name='onboarding_gender'),
    path('onboarding/birthday/', views.onboarding_birthday, name='onboarding_birthday'),
    path('onboarding/bio/', views.onboarding_bio, name='onboarding_bio'),
    path('onboarding/photo/', views.onboarding_photo, name='onaboarding'),
    path('onboarding/finish/', views.onboarding_finish, name='onboarding_finish'),

]