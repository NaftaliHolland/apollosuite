from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(AdminUserCreationForm):
    """
    Form for creating new users in the Django Admin
    """

    class Meta:
        model = CustomUser
        fields = ("email", "phone_number", "first_name", "last_name",)


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating users in the Django admin
    """

    class Meta:
        model = CustomUser
        fields = ("email", "phone_number", "first_name", "last_name",)
