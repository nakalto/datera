from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # model this admin controls
    model = User

    # search & ordering 
    search_fields = ("email", "display_name", "phone")
    ordering = ("email",)

    # columns in the changelist
    list_display = ("email", "display_name", "is_staff", "is_active", "is_superuser")

    # right-side filters (use real fields only)
    list_filter = ("is_staff", "is_superuser", "is_active")

    # horizontal pickers for M2M fields from PermissionsMixin
    filter_horizontal = ("groups", "user_permissions")

    # edit page layout
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("display_name", "phone", "dob", "gender", "seeking")}),
        (_("Verification"), {"fields": ("email_verified", "phone_verified", "twofa_enabled")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # add-user page layout
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_superuser", "is_active", "groups", "user_permissions"),
        }),
    )
