from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from utils.validators import validate_not_in_future

User = get_user_model()

class MapLocation(models.Model):
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.latitude} - {self.longitude}"

class School(models.Model):
    name = models.CharField(max_length=255)
    year_started = models.PositiveIntegerField(validators=[MinValueValidator(1800), validate_not_in_future])
    about = models.TextField()
    website = models.URLField()
    address = models.TextField()
    map_location = models.ForeignKey(MapLocation, on_delete=models.CASCADE, related_name='schools')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    logo_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: write a validator for year started, should not be any year after this year
    # NOTE: will handle this on the frontend for now

    # I need to write a validator to check that the current year is not in the future

    def __str__(self):
        return self.name

class Stream(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='streams')

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'name'],
                name='unique_stream_per_school'
            )
        ]

class Grade(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    # name should be unique per school
    description = models.TextField()
    streams = models.ManyToManyField(Stream, related_name='grades')
    grade_teachers = models.ManyToManyField(User, related_name='grades_managed', blank=True)
    grade_representative = models.ManyToManyField(User, related_name='grades_representing', blank=True, help_text='parents representing classes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'grade'],
                name='unique_grade_per_school'
            )
        ]


    def __str__(self):
        return f"{self.name} ({self.school})"


class StreamTeacher(models.Model):
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name='stream_teachers'
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        related_name='stream_teachers'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='streams_managed'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['grade', 'stream', 'teacher'],
                name='unique_stream_teacher_assignement'
            )
        ]

    def __str__(self):
        return f"{self.teacher} -> {self.stream} ({self.grade})"
