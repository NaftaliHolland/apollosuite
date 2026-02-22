from core.models import AcademicYear, Grade, School, Term
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from users.models import StudentProfile
from decimal import Decimal

from finance.models import (Discount, FeeItem, GradeFeeItem, Payment,
                            PaymentItem, StudentDiscount, StudentFeeAssignment)
from finance.services import (assign_fees_to_student,
                              recalculate_student_discounts)

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
            year_started=timezone.datetime(current_year, 1, 1).date(),
        )
        self.academic_year = AcademicYear.objects.create(
            school=self.school,
            name="2026-2027",
            start_date=timezone.datetime(current_year, 1, 1).date(),
            end_date=timezone.datetime(current_year + 1, 1, 1).date(),
        )
        self.term1 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 3",
            order=3,
            start_date=term_3_start_date,
            end_date=term_3_end_date,
        )
        self.grade1 = Grade.objects.create(school=self.school, name="Grade1")
        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        self.student = StudentProfile.objects.create(
            user=student_user, school=self.school, grade=self.grade1
        )

    def test_per_term_creates_one_per_term(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=400,
            frequency="per_term",
        )

        created = assign_fees_to_student(self.student, self.academic_year)

        self.assertEqual(len(created), 3)
        self.assertEqual(
            StudentFeeAssignment.objects.filter(student=self.student).count(), 3
        )

    def test_yearly_creates_one_in_first_term(self):
        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=activity_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=100,
            frequency="yearly",
        )

        created = assign_fees_to_student(self.student, self.academic_year)

        self.assertEqual(len(created), 1)
        assignment = StudentFeeAssignment.objects.get(
            student=self.student, grade_fee_item=grade_fee_item, term=self.term1
        )

        self.assertEqual(assignment.term, self.term1)

    def test_once_creates_one_with_no_term(self):
        admission_fee_item = FeeItem.objects.create(
            school=self.school, name="Admission"
        )

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=admission_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=2000,
            frequency="one_time",
        )

        created = assign_fees_to_student(self.student, self.academic_year)

        assignment = StudentFeeAssignment.objects.get(
            student=self.student, grade_fee_item=grade_fee_item, term=None
        )

        self.assertIsNone(assignment.term)


class RecalculateStudentDiscountTests(TestCase):
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
            year_started=timezone.datetime(current_year, 1, 1).date(),
        )
        self.academic_year = AcademicYear.objects.create(
            school=self.school,
            name="2026-2027",
            start_date=timezone.datetime(current_year, 1, 1).date(),
            end_date=timezone.datetime(current_year + 1, 1, 1).date(),
        )
        self.term1 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 3",
            order=3,
            start_date=term_3_start_date,
            end_date=term_3_end_date,
        )
        self.grade1 = Grade.objects.create(school=self.school, name="Grade1")
        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        self.student = StudentProfile.objects.create(
            user=student_user, school=self.school, grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        self.tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=300,
            frequency="per_term",
        )

        self.activity_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=activity_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=100,
            frequency="yearly",
        )

        self.student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=self.tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=self.tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=self.tuition_grade_fee_item.amount,
        )

        self.student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=self.activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=self.activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=self.activity_grade_fee_item.amount,
        )

        self.fixed_discount = Discount.objects.create(
            name="100 shillings discount on everything",
            discount_type="general",
            value_type="fixed",
            value=100,
        )

        self.tuition_fixed_discount = Discount.objects.create(
            name="200 shillings discount on tuition",
            discount_type="general",
            value_type="fixed",
            value=200,
            fee_item=tuition_fee_item
        )

        self.percentage_discount = Discount.objects.create(
            name="10% discount on everything",
            discount_type="general",
            value_type="percentage",
            value=10,
        )

        self.tuition_percentage_discount = Discount.objects.create(
            name="10% discount on tuition",
            discount_type="general",
            value_type="percentage",
            value=10,
            fee_item=tuition_fee_item
        )
    
    def test_resets_existing_discount(self):
        self.student_tuition_fee_assignment.discount_amount = 500.00
        self.student_tuition_fee_assignment.net_amount = 3000.00

        self.student_tuition_fee_assignment.save()

        recalculate_student_discounts(self.student, self.academic_year)

        self.student_tuition_fee_assignment.refresh_from_db()

        self.assertEqual(self.student_tuition_fee_assignment.discount_amount, Decimal('0.00'))
        self.assertEqual(self.student_tuition_fee_assignment.net_amount, self.tuition_grade_fee_item)

    def test_percentage_fee_item_discount(self):
        StudentDiscount.objects.create(
            student=self.student,
            discount=self.tuition_percentage_discount,
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        self.student_tuition_fee_assignment.refresh_from_db()

        self.assertEqual(self.student_tuition_fee_assignment.discount_amount, Decimal('30.00'))
        self.assertEqual(self.student_tuition_fee_assignment.net_amount, Decimal('270.00'))

        self.student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(self.student_tuition_fee_assignment.discount_amount, Decimal('0.00'))


    def test_fixed_total_discount_distributed_proportionally(self):
        StudentDiscount.objects.create(
            student=self.student,
            discount=self.fixed_discount, # 100 from gross
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        self.student_tuition_fee_assignment.refresh_from_db()
        self.student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(self.student_tuition_fee_assignment.discount_amount, Decimal('75.00'))
        self.assertEqual(self.student_activity_fee_assignment.dicount_amount, Decimal('25.00'))

        self.assertEqual(self.student_tuition_fee_assignment.net_amount, Decimal('225.00'))
        self.assertEqual(self.student_activity_fee_assignment.net_amount, Decimal('75.00'))


    def test_combined_fee_item_and_total_discount(self):
        StudentDiscount.objects.create(
            student=self.student,
            discount=self.percentage_discount, # This is on gross
            academic_year=self.academic_year,
        )

        StudentDiscount.objects.create(
            student=self.student,
            discount=self.tuition_percentage_discount,
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        self.student_tuition_fee_assignment.refresh_from_db()
        self.student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(self.student_tuition_fee_assignment.discount_amount, Decimal('20.00'))
        self.assertEqual(self.student_activity_fee_assignment.dicount_amount, Decimal('30.00'))

        self.assertEqual(self.student_tuition_fee_assignment.net_amount, Decimal('80.00'))
        self.assertEqual(self.student_activity_fee_assignment.net_amount, Decimal('270.00'))


    
    def test_raises_if_net_amount_goes_negative(self):
        way_too_big_discount = Discount.objects.create(
            name="Way too big",
            discount_type="general",
            value_type="fixed",
            value=200000,
        )

        StudentDiscount.objects.create(
            student=self.student,
            discount=self.percentage_discount, # This is on gross
            academic_year=self.academic_year,
        )

        with self.assertRaises(ValidationError):
            recalculate_student_discounts(self.student, self.academic_year)


    def test_idempotent(self):
        StudentDiscount.objects.create(
            student=self.student,
            discount=self.percentage_discount, # This is on gross
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        first_snapshot = list(
            StudentFeeAssignment.objects
            .filter(student=self.student)
            .values_list("discount_amount", flat=True)
        )

        recalculate_student_discounts(self.student, self.academic_year)

        second_snapshot = list(
            StudentFeeAssignment.objects
            .filter(student=self.student)
            .values_list("discount_amount", flat=True)
        )

        self.assertEqual(first_snapshot, second_snapshot)
