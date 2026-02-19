from django.db import transaction
from django.db.models import Max

from users.models import StudentProfile


def generate_admission_number(school):
    # Use a transaction to avoid race conditions
    with transaction.atomic():
        max_adm = StudentProfile.objects.select_for_update().filter(
            school=school
        ).aggregate(max_number=Max('admission_number'))['max_number']
        
        next_number = int(max_adm) + 1 if max_adm else 1
        return f"{next_number:04d}"
