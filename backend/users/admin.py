from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Admin interface for the custom user model.
    Customizes the Django admin to work with email-based authentication and removes
    username-related fields from the interface
    """

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    ]

    # Filters available in the right sidebar
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
    )

    # TODO: I need to test this out
    # Layout for the user detail/edit page
    fieldsets = (
        (None, {"fields": ("phone_number",  "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    # Layout for the add user page
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    # Enable search by email
    search_fields = ("email", "phone_number", "first_name", "last_name")

    # Default ordering in the list view
    ordering = ("email",)


# Register the custom user model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
