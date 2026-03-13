from datetime import date

from django.core.exceptions import ValidationError

def validate_school_start(value):
    if value > date.today():
        raise ValidationError("Start date cannot be in the future")
    if value < date(1600, 1, 1):
        raise ValidationError("Start date too far in the past")

def validate_not_in_the_future(value):
    if value > date.today():
        raise ValidationError("Date cannot be in the future")
