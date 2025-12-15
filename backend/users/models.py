from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

#from core.models import School


class CustomUserManager(BaseUserManager):
    """
    custom user manager for phone_number or email based authentication
    """

    def create_user(self, phone_number, password, email=None, **extra_fields):

        if not email and not phone_number:
            raise ValidationError("User must have an email or phone number")

        # What does normalize_email do?? Can I write that for my phone number??
        email = self.normalize_email(email)
        roles = extra_fields.pop("roles")
        schools = extra_fields.pop("schools")
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()

        user.roles.set(roles)
        user.schools.set(schools)

        return user

    def create_superuser(self, phone_number, password, email=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        if extra_fields.get("is_staff") is not True:
          raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
          raise ValueError("Superuser must have is_superuser=True.")
         
        return self.create_user(phone_number, password, email, **extra_fields)


class Role(models.Model):
    school = models.ForeignKey('core.School', on_delete=models.CASCADE, related_name='roles', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    USER_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    username = None
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)

    schools = models.ManyToManyField('core.School', related_name="users", blank=True)
    roles = models.ManyToManyField(Role, related_name='users')
    status = models.CharField(max_length=50, choices=USER_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: Write validation for phone number
    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
