from datetime import date

from django.core.exceptions import ValidationError


def validate_not_in_future(value):
    current_year = date.today().year
    if value > current_year:
        raise ValidationError("Year started cannot be in the future.")
