from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, UserPhoto
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()   # Safely get the active User model (works with custom user models)


# ONBOARDING FLOW

# Step 1: Collect user's name
def onboarding_name(request):
    if request.method == 'POST':
        # Save name into session dictionary
        request.session['onboarding'] = {"name": request.POST.get("name")}
        return redirect("profiles:onboarding_gender")
    # Render template with progress bar at 20%
    return render(request, 'profiles/onboarding/name.html', {"progress": 20})


# Step 2: Collect user's gender
def onboarding_gender(request):
    if request.method == 'POST':
        data = request.session.get('onboarding', {})
        data['gender'] = request.POST.get('gender')   # "M" or "F"
        request.session['onboarding'] = data
        return redirect("profiles:onboarding_birthday")
    return render(request, 'profiles/onboarding/gender.html', {"progress": 40})


# Step 3: Collect user's birthday
def onboarding_birthday(request):
    if request.method == 'POST':
        data = request.session.get('onboarding', {})
        data['birthday'] = request.POST.get('birthday')   # Expect format YYYY-MM-DD
        request.session['onboarding'] = data
        return redirect("profiles:onboarding_bio")
    return render(request, 'profiles/onboarding/birthday.html', {"progress": 60})


# Step 4: Collect user's bio
def onboarding_bio(request):
    if request.method == 'POST':
        data = request.session.get('onboarding', {})
        data['bio'] = request.POST.get('bio')
        request.session['onboarding'] = data
        return redirect("profiles:onboarding_looking_for")
    return render(request, 'profiles/onboarding/bio.html', {"progress": 70})


# Step 5: Collect user's preference (looking for men/women/all)
def onboarding_looking_for(request):
    if request.method == 'POST':
        data = request.session.get('onboarding', {})
        data['looking_for'] = request.POST.get('looking_for')   # "M", "F", or "A"
        request.session['onboarding'] = data
        return redirect("profiles:onboarding_goal")
    return render(request, 'profiles/onboarding/looking_for.html', {"progress": 80})


# Step 6: Collect relationship goal
def onboarding_goal(request):
    if request.method == 'POST':
        data = request.session.get('onboarding', {})
        data['relationship_goal'] = request.POST.get('relationship_goal')   # e.g. "longterm"
        request.session['onboarding'] = data
        return redirect("profiles:onboarding_photo")
    return render(request, 'profiles/onboarding/goal.html', {"progress": 90})


# Step 7: Collect user's photo
@login_required
def onboarding_photo(request):
    if request.method == 'POST':
        photo = request.FILES.get("photo")
        if photo:
            # Ensure profile exists
            profile, _ = Profile.objects.get_or_create(user=request.user)
            # Save the uploaded photo right away
            UserPhoto.objects.create(profile=profile, image=photo)
        # Move on to the finish step
        return redirect("profiles:onboarding_finish")
    return render(request, 'profiles/onboarding/photo.html', {"progress": 100})

# Final step: Save everything into Profile + UserPhoto
@login_required
def onboarding_finish(request):
    data = request.session.get("onboarding", {})
    user = request.user

    # Get or create profile for this user
    profile, _ = Profile.objects.get_or_create(user=user)

    # Save collected fields
    profile.full_name = data.get("name")
    profile.gender = data.get("gender")
    profile.bio = data.get("bio")
    profile.looking_for = data.get("looking_for")
    profile.relationship_goal = data.get("relationship_goal")

    # Parse birthday safely
    birthday_str = data.get("birthday")
    if birthday_str:
        try:
            profile.birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid birthday format: {birthday_str}")

    # Mark onboarding complete
    profile.onboarding_complete = True
    profile.save()

    # Clear session data
    request.session.pop("onboarding", None)

    return redirect("accounts:dashboard")

    

