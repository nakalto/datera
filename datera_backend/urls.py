"""
URL configuration for datera_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# datera_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # API routes
    path("api/auth/", include("accounts.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/media/", include("mediahub.urls")),
    path("api/chat/", include("messaging.urls")),


    # Frontend template routes
    path("auth/login/", TemplateView.as_view(template_name="auth/login.html")),
    path("auth/register/", TemplateView.as_view(template_name="auth/register.html")),
    path("auth/verify-email/", TemplateView.as_view(template_name="auth/verify_email.html")),
    path("auth/verify-phone/", TemplateView.as_view(template_name="auth/verify_phone.html")),
    path("auth/2fa/", TemplateView.as_view(template_name="auth/2fa.html")),
    path("dashboard/", login_required(TemplateView.as_view(template_name="dashboard.html"))),
    path("discover/", TemplateView.as_view(template_name="discover.html")),
    path("profile/edit/", TemplateView.as_view(template_name="profile_edit.html")),
    path("discover/", TemplateView.as_view(template_name="discover.html")),
]

# serving uploaded media files in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
