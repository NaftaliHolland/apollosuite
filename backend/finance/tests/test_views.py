from core.models import School
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

User = get_user_model()


#class FeeItemViewSetTest(APITestCase):
#
#    def setUp(self):
#       self.user = User.objects.create_user(
#            first_name="John",
#            last_name="Doe",
#            phone_number="0798282343",
#            password="unsecurePass123",
#        )
#
#        current_year = timezone.now().year
#
#        term_1_start_date = timezone.datetime(current_year, 1, 1)
#        term_1_end_date = timezone.datetime(current_year, 4, 1)
#
#        term_2_start_date = timezone.datetime(current_year, 5, 1)
#        term_2_end_date = timezone.datetime(current_year, 7, 1)
#
#        term_3_start_date = timezone.datetime(current_year, 9, 1)
#        term_3_end_date = timezone.datetime(current_year, 11, 1)
#
#        self.school = School.objects.create(
#            name="Acme School",
#            year_started=timezone.datetime(current_year, 1, 1).date(),
#        )
#
#        self.client.force_authenticate(self.user)
