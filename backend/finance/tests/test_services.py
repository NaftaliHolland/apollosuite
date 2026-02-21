from core.models import AcademicYear, Grade, School, Term
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from users.models import StudentProfile

from finance.models import (Discount, FeeItem, GradeFeeItem, Payment,
                            PaymentItem, StudentDiscount, StudentFeeAssignment)
from finance.services import assign_fees_to_student

User = get_user_model()

class AssignFeeToStudentTest(TestCase):
    def setUp(self):

        current_year = timezone.now().year

        term_1_start_date = timezone.datetime(current_year, 1, 1)
        term_1_end_date = timezone.datetime(current_year, 4, 1)

        term_2_start_date = timezone.datetime(current_year, 5, 1)
        term_2_end_date = timezone.datetime(current_year, 7, 1)

        term_3_start_date = timezone.datetime(current_year, 9, 1)
        term_3_end_date = timezone.datetime(current_year, 11, 1)

        self.school = School.objects.create(
            name="Acme School",
            year_started=timezone.datetime(current_year, 1, 1).date()
        )
        self.academic_year = AcademicYear.objects.create(
            school=self.school,
            name="2026-2027",
            start_date=timezone.datetime(current_year, 1, 1).date(),
            end_date=timezone.datetime(current_year + 1, 1, 1).date()
        )
        self.term1 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date)
        self.term2 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date)
        self.term3 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 3",
            order=3,
            start_date=term_3_start_date,
            end_date=term_3_end_date)
        self.grade1 = Grade.objects.create(
            school=self.school,
            name="Grade1"
        )
        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123"
        )
        self.student = StudentProfile.objects.create(
            user=student_user,
            school=self.school
        )

    def test_per_term_creates_one_per_term(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        grade_fee_item = GradeFeeItem(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term"
        )

        created = assign_fees_to_student(self.student, self.academic_year)

        self.assertEqual(len(created), 3)
        self.assetEqual(
            StudentFeeAssignment.objects.filter(student=self.student).count(), 3
        )

    def test_yearly_creates_one_in_first_term(self):
        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        grade_fee_item = GradeFeeItem(
            fee_item=activity_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=500,
            frequency="yearly"
        )

        created = assign_fees_to_student(self.student, self.academic_year)

        self.assertEqual(len(created), 1)
        assignment = StudentFeeAssignment.objects.get(student=self.student, grade_fee_item=grade_fee_item, term=self.term1)

        self.assertEqual(assignment.term, self.term1)

    def test_once_creates_one_with_no_term(self):
        admission_fee_item = FeeItem.objects.create(school=self.school, name="Admission")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=admission_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=2000,
            frequency="one_time"
        )

        created = assign_fees_to_student(self.student, self.academic_year)

        assignment = StudentFeeAssignment.objects.get(student=self.student, grade_fee_item=grade_fee_item, term=self.term1)

        self.assertIsNone(assignment.term)
