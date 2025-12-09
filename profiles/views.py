from django.shortcuts import render, redirect
from .models import Profile

# Step 1: Collect user's name
def onboarding_name(request):
    if request.method == 'POST':
        # Save name into session dictionary
        request.session['onboarding'] = {
            "name": request.POST.get("name")
        }
        # Redirect to next step (gender)
        return redirect("onboarding_gender")

    # Render name input form with progress indicator
    return render(request, 'profiles/onboarding/name.html', {"progress": 20})


# Step 2: Collect user's gender
def onboarding_gender(request):
    if request.method == 'POST':
        # Retrieve existing onboarding data from session
        data = request.session.get('onboarding', {})
        # Add gender to session data
        data['gender'] = request.POST.get('gender')
        request.session['onboarding'] = data
        # Redirect to next step (birthday)
        return redirect("onboarding_birthday")

    # Render gender input form with progress indicator
    return render(request, 'profiles/onboarding/gender.html', {"progress": 40})


# Step 3: Collect user's birthday
def onboarding_birthday(request):
    if request.method == 'POST':
        # Retrieve existing onboarding data
        data = request.session.get('onboarding', {})
        # Add birthday to session data
        data['birthday'] = request.POST.get('birthday')
        request.session['onboarding'] = data
        # Redirect to next step (bio)
        return redirect("onboarding_bio")

    # Render birthday input form with progress indicator
    return render(request, 'profiles/onboarding/birthday.html', {"progress": 60})


# Step 4: Collect user's bio
def onboarding_bio(request):
    if request.method == 'POST':
        # Retrieve existing onboarding data
        data = request.session.get('onboarding', {})
        # Add bio to session data
        data['bio'] = request.POST.get('bio')
        request.session['onboarding'] = data
        # Redirect to next step (photo upload)
        return redirect("onboarding_photo")

    # Render bio input form with progress indicator
    return render(request, 'profiles/onboarding/bio.html', {"progress": 80})


# Step 5: Collect user's photo
def onboarding_photo(request):
    if request.method == 'POST':
        # Retrieve existing onboarding data
        data = request.session.get('onboarding', {})

        # Handle photo upload
        photo = request.FILES.get("photo")
        if photo:
            # Save photo filename in session (for now)
            request.session["uploaded_photo"] = photo.name

        # Save updated data back into session
        request.session['onboarding'] = data
        # Redirect to final step (finish)
        return redirect("onboarding_finish")

    # Render photo upload form with progress indicator
    return render(request, 'profiles/onboarding/photo.html', {"progress": 100})

def onboarding_finish(request):
    # Get collected data from session
    data = request.session.get('onboarding', {})
    photo_name = request.session.get('uploaded_photo')

    # Get or create profile for this user
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Save session data into profile fields
    profile.name = data.get("name")
    profile.gender = data.get("gender")
    profile.bio = data.get("bio")

    # Birthday needs conversion from string to date
    if data.get("birthday"):
        from datetime import datetime
        try:
            profile.birthday = datetime.strptime(data.get("birthday"), "%Y-%m-%d").date()
        except ValueError:
            pass  # ignore invalid date format

    # For now, just store photo filename (real upload handling later)
    if photo_name:
        profile.photo.name = f"profiles/photos/{photo_name}"

    # Mark onboarding as complete
    profile.completed = True
    profile.save()

    # Clear session data
    request.session.pop('onboarding', None)
    request.session.pop('uploaded_photo', None)

    # Render finish screen
    return render(request, 'profiles/onboarding/finish.html', {"profile": profile})