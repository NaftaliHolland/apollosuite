from django.db import transaction
from users.models import AdminProfile

from core.models import School


def assign_admin_to_school(user, school):
    admin, _= AdminProfile.objects.get_or_create(user=user)

    admin.schools.add(school)

    return admin
