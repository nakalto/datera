from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, UserPhoto
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404


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
    # Get onboarding data from session
    data = request.session.get("onboarding", {})
    user = request.user

    # Get or create profile for this user
    profile, _ = Profile.objects.get_or_create(user=user)

    # Save collected fields
    profile.full_name = data.get("name")
    profile.bio = data.get("bio")

    # Map full words to short codes
    gender_map = {"Male": "M", "Female": "F"}
    looking_for_map = {"Men": "M", "Women": "F", "All": "A"}
    relationship_goal_map = {
        "Long-term partner": "LT",
        "Serious daters": "SR",
        "Free tonight": "FT",
        "Short-term fun": "ST",
        "Friendship": "FR",
        "Not sure yet": "UN",
    }

    # Apply mappings safely
    gender_value = data.get("gender")
    looking_for_value = data.get("looking_for")
    relationship_goal_value = data.get("relationship_goal")

    if gender_value in gender_map:
        profile.gender = gender_map[gender_value]

    if looking_for_value in looking_for_map:
        profile.looking_for = looking_for_map[looking_for_value]

    if relationship_goal_value in relationship_goal_map:
        profile.relationship_goal = relationship_goal_map[relationship_goal_value]

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

    return redirect("profiles:dashboard")

    


@login_required
def dashboard(request):
    profile = request.user.profile   # Current user's profile

    # Base queryset: all other onboarded profiles
    profiles = (
        Profile.objects
        .filter(onboarding_complete=True)
        .exclude(user=request.user)
        .select_related("user")
        .prefetch_related("photos")
    )

    # Apply gender filter only if preference is M or F
    if profile.looking_for == "M":
        profiles = profiles.filter(gender="M")
    elif profile.looking_for == "F":
        profiles = profiles.filter(gender="F")
    # If "A" (All), no filter applied

    return render(
        request,
        "profiles/dashboard.html",
        {
            "profile": profile,             # current user profile
            "profiles": profiles,           # other profiles
            "my_photos": profile.photos.all()  # current user's photos
        }
    )


# --------------------------------------------
# Import Django shortcuts and pagination tools
# --------------------------------------------

@login_required
def explore(request):
    """
    Explore view:
    - Default: shows goal-driven categories with counts
    - If ?goal= is provided, shows profiles in that category
    - Supports pagination for profile lists
    """

    # Read ?goal= parameter from URL (e.g. ?goal=LT)
    goal = request.GET.get("goal")
    page_number = request.GET.get("page", 1)

    if goal:
        # Show profiles for selected goal
        profiles_qs = Profile.objects.filter(
            relationship_goal=goal,          # must match one of: LT, SR, FT, ST, FR, UN
            onboarding_complete=True
        ).select_related("user").prefetch_related("photos")

        # Paginate results (10 profiles per page)
        paginator = Paginator(profiles_qs, 10)
        profiles = paginator.get_page(page_number)

        return render(
            request,
            "profiles/explore.html",
            {
                "profiles": profiles,   # Paginated profiles
                "goal": goal            # Current goal for heading + pagination links
            }
        )
    else:
        # Show counts for all goals (using codes)
        goals = {
            "LT": Profile.objects.filter(relationship_goal="LT", onboarding_complete=True).count(),
            "SR": Profile.objects.filter(relationship_goal="SR", onboarding_complete=True).count(),
            "FT": Profile.objects.filter(relationship_goal="FT", onboarding_complete=True).count(),
            "ST": Profile.objects.filter(relationship_goal="ST", onboarding_complete=True).count(),
            "FR": Profile.objects.filter(relationship_goal="FR", onboarding_complete=True).count(),
            "UN": Profile.objects.filter(relationship_goal="UN", onboarding_complete=True).count(),
        }

        return render(request, "profiles/explore.html", {"goals": goals})



@login_required
def profile(request):
    """
    Profile view:
    - Shows the logged-in user's profile details
    - Can later allow editing
    """
    return render(
        request,
        "profiles/profile.html",
        {"user": request.user}
    )

def profile_view(request, user_id):
    partner = get_object_or_404(User, id=user_id)
    return render(request, "profiles/profile_view.html", {"partner": partner})



# Long-term Partner Dashboard
@login_required  # Require user to be logged in
def long_term_dashboard(request):
    # Query all profiles with relationship_goal = "LT" and onboarding complete
    profiles_qs = Profile.objects.filter(
        relationship_goal="LT", onboarding_complete=True
    ).select_related("user").prefetch_related("photos")  # Optimize queries

    # Paginate results, 10 profiles per page
    paginator = Paginator(profiles_qs, 10)
    profiles = paginator.get_page(request.GET.get("page", 1))  # Get current page

    # Render template with paginated profiles
    return render(request, "profiles/long_term_dashboard.html", {"profiles": profiles})


# Serious Daters Dashboard
@login_required
def serious_daters_dashboard(request):
    # Query profiles with relationship_goal = "SR"
    profiles_qs = Profile.objects.filter(
        relationship_goal="SR", onboarding_complete=True
    ).select_related("user").prefetch_related("photos")

    # Paginate results
    paginator = Paginator(profiles_qs, 10)
    profiles = paginator.get_page(request.GET.get("page", 1))

    # Render template
    return render(request, "profiles/serious_daters_dashboard.html", {"profiles": profiles})



# Free Tonight Dashboard
@login_required
def free_tonight_dashboard(request):
    # Query profiles with relationship_goal = "FT"
    profiles_qs = Profile.objects.filter(
        relationship_goal="FT", onboarding_complete=True
    ).select_related("user").prefetch_related("photos")

    # Paginate results
    paginator = Paginator(profiles_qs, 10)
    profiles = paginator.get_page(request.GET.get("page", 1))

    # Render template
    return render(request, "profiles/free_tonight_dashboard.html", {"profiles": profiles})



# Short-term Fun Dashboard
@login_required
def short_term_dashboard(request):
    # Query profiles with relationship_goal = "ST"
    profiles_qs = Profile.objects.filter(
        relationship_goal="ST", onboarding_complete=True
    ).select_related("user").prefetch_related("photos")

    # Paginate results
    paginator = Paginator(profiles_qs, 10)
    profiles = paginator.get_page(request.GET.get("page", 1))

    # Render template
    return render(request, "profiles/short_term_dashboard.html", {"profiles": profiles})



# Friendship Dashboard
@login_required
def friendship_dashboard(request):
    # Query profiles with relationship_goal = "FR"
    profiles_qs = Profile.objects.filter(
        relationship_goal="FR", onboarding_complete=True
    ).select_related("user").prefetch_related("photos")

    # Paginate results
    paginator = Paginator(profiles_qs, 10)
    profiles = paginator.get_page(request.GET.get("page", 1))

    # Render template
    return render(request, "profiles/friendship_dashboard.html", {"profiles": profiles})



# Not Sure Yet Dashboard
@login_required
def unsure_dashboard(request):
    # Query profiles with relationship_goal = "UN"
    profiles_qs = Profile.objects.filter(
        relationship_goal="UN", onboarding_complete=True
    ).select_related("user").prefetch_related("photos")

    # Paginate results
    paginator = Paginator(profiles_qs, 10)
    profiles = paginator.get_page(request.GET.get("page", 1))

    # Render template
    return render(request, "profiles/unsure_dashboard.html", {"profiles": profiles})
