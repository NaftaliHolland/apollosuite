from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from utils.generate_fake_phone import generate_fake_phone

#from core.models import School

class CustomUserManager(BaseUserManager):
    """
    custom user manager for phone_number or email based authentication
    """

    def create_user(self, phone_number, password=None, email=None, **extra_fields):

        if not email and not phone_number:
            raise ValidationError("User must have an email or phone number")

        # TODO: What does normalize_email do?? Can I write that for my phone number??

        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()

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
    def is_admin(self):
        return hasattr(self, "adminprofile")

    @property
    def roles(self):
        current_roles = []

        if self.is_student:
            current_roles.append("student")
        if self.is_parent:
            current_roles.append("parent")
        if self.is_teacher:
            current_roles.append("teacher")
        if self.is_school_staff:
            current_roles.append("school_staff")
        if self.is_admin:
            current_roles.append("admin")

    def belongs_to_school(self, school_id):
        if hasattr(self, "studentprofile"):
            return self.studentprofile.school_id == school_id

        # TODO: Do this for all profiles
        if hasattr(self, "adminprofile"):
            return self.adminprofile.schools.filter(id=school_id).exists()

        if hasattr(self, "staffprofile"):
            return self.staffprofile.schools.filter(id=school_id).exists()

        return False

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='adminprofile')
    schools = models.ManyToManyField('core.School', related_name="admins", blank=True)

class StudentProfile(models.Model):

    ENROLMENT_STATUS_CHOICES = [
        ("applied", "Applied"),
        ("enrolled", "Enrolled"),
        ("transferred", "Transferred"),
        ("graduated", "Graduated"),
        ("expelled", "Expelled"),
        ("withdrawn", "Withdrawn"),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='studentprofile')
    school = models.ForeignKey("core.School", related_name="students", on_delete=models.CASCADE)
    grade = models.ForeignKey('core.Grade', on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    stream = models.ForeignKey('core.Stream', on_delete=models.CASCADE, related_name='stream', null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    enrollment_status = models.CharField(max_length=20, choices=ENROLMENT_STATUS_CHOICES, default="applied")
    transfered_from = models.CharField(null=True, blank=True, help_text='school the student transffered from')

    admission_number = models.CharField(max_length=255)
    # NOTE: I need to figure out an algorithm for generating admission numbers
    assessment_number = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StudentProfile({self.user.first_name} - {self.user.last_name})"

class ParentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='parentprofile')
    schools = models.ManyToManyField('core.School', related_name="parents", blank=True)

    #TODO: Add other fields

    def __str__(self):
        return f"ParentProfile({self.user.first_name - self.user.last_name})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='teacherprofile')
    schools = models.ManyToManyField('core.School', related_name="teachers", blank=True)

    #TODO: Add other fields

    def __str__(self):
        return f"TeacherProfile({self.user.first_name - self.user.last_name})"


class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="staffprofile")
    schools = models.ManyToManyField('core.School', related_name="staff", blank=True)

    #TODO: Add other fields

    def __str__(self):
        return f"StaffProfile({self.user.first_name - self.user.last_name})"
