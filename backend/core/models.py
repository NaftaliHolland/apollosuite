from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from utils.validators import validate_school_start

User = get_user_model()

class MapLocation(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.latitude} - {self.longitude}"


class School(models.Model):
    name = models.CharField(max_length=255)
    year_started = models.DateField(validators=[validate_school_start])
    about = models.TextField()
    website = models.URLField()
    address = models.TextField()
    map_location = models.ForeignKey(MapLocation, on_delete=models.CASCADE, related_name='schools', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_schools")
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    logo_url = models.CharField(max_length=500, blank=True, null=True)
    # TODO: add added_by field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Stream(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='streams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'name'],
                name='unique_stream_per_school'
            )
        ]

    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '').lower()

        super().save(*args, **kwargs)

class Grade(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    streams = models.ManyToManyField(Stream, related_name='grades', blank=True)
    grade_teachers = models.ManyToManyField(User, related_name='grades_managed', blank=True)
    grade_representatives = models.ManyToManyField(User, related_name='grades_representing', blank=True, help_text='parents representing classes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'name'],
                name='unique_grade_per_school'
            )
        ]

    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '').lower()

        super().save(*args, **kwargs)

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


class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'name'],
                name='unique_academic_year_per_school',
                violation_error_code=409,
                violation_error_message="An academic year with the same name exists"

            )
        ]

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Academic year start date must be before end_date")

    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '').lower()

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.start_date} : {self.end_date}"


class Term(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='terms')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'academic_year', 'name'],
                name='unique_term_name_per_year'
            )
        ]

    def clean(self): # Since I'm using DRF, I'll need to call full_clean somewhere
        academic_year = self.academic_year
        if self.start_date < academic_year.start_date or self.end_date > academic_year.end_date:
            raise ValidationError(
                'Term dates must fall within the academic year'
            )

        overlapping_terms = (
            Term.objects.filter(academic_year=academic_year)
            .exclude(pk=self.pk)
            .filter(
                start_date__lt=self.end_date,
                end_date__gt=self.start_date
            )
        )

        if overlapping_terms.exists():
            raise ValidationError("Term dates overlap with another term")


    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '').lower()

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"
