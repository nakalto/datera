from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    # Step 1: Name
    path("onboarding/name/", views.onboarding_name, name="onboarding_name"),

    # Step 2: Gender
    path("onboarding/gender/", views.onboarding_gender, name="onboarding_gender"),

    # Step 3: Birthday
    path("onboarding/birthday/", views.onboarding_birthday, name="onboarding_birthday"),

    # Step 4: Bio
    path("onboarding/bio/", views.onboarding_bio, name="onboarding_bio"),

    # Step 5: Looking For (men/women/all)
    path("onboarding/looking-for/", views.onboarding_looking_for, name="onboarding_looking_for"),

    # Step 6: Relationship Goal (longterm, serious, etc.)
    path("onboarding/goal/", views.onboarding_goal, name="onboarding_goal"),

    # Step 7: Photo
    path("onboarding/photo/", views.onboarding_photo, name="onboarding_photo"),

    # Final Step: Finish onboarding
    path("onboarding/finish/", views.onboarding_finish, name="onboarding_finish"),
]
