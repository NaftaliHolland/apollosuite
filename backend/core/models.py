from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date


class MapLocation(models.Model):
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.latitude} - {self.longitude}"

class School(models.Model):
    name = models.CharField(max_length=255)
    year_started = models.PositiveIntegerField(validators=[MinValueValidator(1800)])
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

    def clean(self):
        current_year = date.today().year
        # TODO: test this
        if self.year_started > current_year:
            raise ValidationError("year_started cannot be in the future")

    def __str__(self):
        return self.name
