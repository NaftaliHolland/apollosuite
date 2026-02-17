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
        #roles = extra_fields.pop("roles", None)
        schools = extra_fields.pop("schools", None)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()

        #if roles:
        #    user.roles.set(roles)

        if schools:
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


#class Role(models.Model):
#    school = models.ForeignKey('core.School', on_delete=models.CASCADE, related_name='roles', null=True, blank=True)
#    name = models.CharField(max_length=100)
#    description = models.TextField(blank=True, null=True)
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)
#
#    def __str__(self):
#        return self.name

class CustomUser(AbstractUser):
    USER_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    GENDER_CHOICES = [
        ('m', "Male"),
        ('f', "Female"),
    ]

    username = None
    email = models.EmailField(unique=True, null=True, blank=True)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20, unique=True)

    schools = models.ManyToManyField('core.School', related_name="users", blank=True)
    #roles = models.ManyToManyField(Role, related_name='users', blank=True)
    status = models.CharField(max_length=50, choices=USER_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: Write validation for phone number
    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    @property
    def is_student(self):
        return hasattr(self, "studentprofile")

    @property
    def is_teacher(self):
        return hasattr(self, "teacherprofile")

    @property
    def is_parent(self):
        return hasattr(self, "parentprofile")

    @property
    def is_school_staff(self):
        return hasattr(self, "staffprofile")

    @property
    def roles(self):
        current_roles = []

        if self.is_student:
            current_roles.append("student")
        if self.is_parent:
            current_roles.append("parent")
        if self.is_teacher:
            current_roles.append("teacher")
        if self.is_staff:
            current_roles.append("staff")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='studentprofile')
    grade = models.ForeignKey('core.Grade', on_delete=models.CASCADE, related_name='student_profile')
    stream = models.ForeignKey('core.Stream', on_delete=models.CASCADE, related_name='stream')
    enrollment_date = models.DateField()
    transfered_from = models.CharField(null=True, blank=True, help_text='school the student transffered from')

    admission_number = models.CharField(max_length=255)
    # NOTE: I need to figure out an algorithm for generating admission numbers
    assesment_number = models.CharField(max_length=255)

    def __str__(self):
        return f"StudentProfile({self.user.first_name - self.user.last_name})"

class ParentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='parentprofile')

    #TODO: Add other fields

    def __str__(self):
        return f"ParentProfile({self.user.first_name - self.user.last_name})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='teacherprofile')

    #TODO: Add other fields

    def __str__(self):
        return f"TeacherProfile({self.user.first_name - self.user.last_name})"


class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="staffprofile")

    #TODO: Add other fields

    def __str__(self):
        return f"StaffProfile({self.user.first_name - self.user.last_name})"
