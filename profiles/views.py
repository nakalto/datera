from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
User = get_user_model()


# Step 1: Collect user's name
def onboarding_name(request):
    if request.method == 'POST':
        # Save name into session dictionary
        request.session['onboarding'] = {
            "name": request.POST.get("name")
        }
        # Redirect to next step (gender)
        return redirect("profiles:onboarding_gender")

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
        return redirect("profiles:onboarding_birthday")

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
        return redirect("profiles:onboarding_bio")

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
        return redirect("profiles:onboarding_photo")

    # Render bio input form with progress indicator
    return render(request, 'profiles/onboarding/bio.html', {"progress": 80})


# Step 5: Collect user's photo
def onboarding_photo(request):
    if request.method == 'POST':
        # Retrieve existing onboarding data from session
        data = request.session.get('onboarding', {})

        # Handle photo upload
        photo = request.FILES.get("photo")
        if photo:
            # Save the actual file object into the User model directly
            user = request.user
            user.profile_photo = photo   # Django saves file into MEDIA_ROOT/profile_photos/
            user.save()

        # Save updated data back into session (for consistency with other steps)
        request.session['onboarding'] = data

        # Redirect to final step (finish)
        return redirect("profiles:onboarding_finish")

    # Render photo upload form with progress indicator
    return render(request, 'profiles/onboarding/photo.html', {"progress": 100})


def onboarding_finish(request):
    """
    Final step of onboarding:
    - Collect data from session
    - Save into User model
    - Handle birthday conversion
    - Save uploaded photo properly
    - Mark onboarding complete
    """

    # Retrieve collected onboarding data from session
    data = request.session.get("onboarding", {})
    user = request.user  # Current logged-in user

    # Save text fields into User model
    user.full_name = data.get("name")
    user.gender = data.get("gender")
    user.bio = data.get("bio")

    # Convert birthday string into a proper date object
    birthday_str = data.get("birthday")
    if birthday_str:
        from datetime import datetime
        try:
            # Expecting format YYYY-MM-DD from <input type="date">
            user.birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        except ValueError:
            # Log invalid format for debugging instead of silently ignoring
            print(f"Invalid birthday format received: {birthday_str}")

    # Save uploaded photo (if provided)
    photo = request.FILES.get("photo")
    if photo:
        user.profile_photo = photo  # Django saves file into MEDIA_ROOT/profile_photos/

    # Mark onboarding as complete
    user.onboarding_complete = True

    # Save all changes in one go
    user.save()

    # Clear session data
    request.session.pop("onboarding", None)

    # Redirect to dashboard/home
    return redirect("accounts:dashboard")

