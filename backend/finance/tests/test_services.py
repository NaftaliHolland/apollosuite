from core.models import AcademicYear, Grade, School, Term
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from users.models import StudentProfile

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
            user=student_user,
            school=self.school,
            grade=self.grade1
        )


    def test_per_term_creates_one_per_term(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
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
            amount=500,
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

        #self.tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")
        #self.activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        #self.tuition_grade_fee_item = GradeFeeItem.objects.create(
        #    fee_item=self.tuition_fee_item,
        #    grade=self.grade1,
        #    academic_year=self.academic_year,
        #    amount=3500,
        #    frequency="per_term",
        #)

        #self.activity_grade_fee_item = GradeFeeItem.objects.create(
        #    fee_item=self.activity_fee_item,
        #    grade=self.grade1,
        #    academic_year=self.academic_year,
        #    amount=200,
        #    frequency="yearly",
        #)

        #self.student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
        #    student=self.student,
        #    grade_fee_item=self.tuition_grade_fee_item,
        #    term=self.term1,
        #    academic_year=self.academic_year,
        #    gross_amount=self.tuition_grade_fee_item.amount,
        #    discount_amount=0,
        #    net_amount=self.tuition_grade_fee_item.amount,
        #)

        #self.student_activity_fee_assignment = StudentFeeAssignment.objects.create(
        #    student=self.student,
        #    grade_fee_item=self.activity_grade_fee_item,
        #    term=self.term1,
        #    academic_year=self.academic_year,
        #    gross_amount=self.activity_grade_fee_item.amount,
        #    discount_amount=0,
        #    net_amount=self.activity_grade_fee_item.amount,
        #)

        #self.fixed_discount = Discount.objects.create(
        #    name="500 shillings discount on everything",
        #    discount_type="general",
        #    value_type="fixed",
        #    value=500,
        #)

        #self.tuition_fixed_discount = Discount.objects.create(
        #    name="200 shillings discount on tuition",
        #    discount_type="general",
        #    value_type="fixed",
        #    value=200,
        #    fee_item=self.tuition_fee_item
        #)

        #self.percentage_discount = Discount.objects.create(
        #    name="10% discount on everything",
        #    discount_type="general",
        #    value_type="percentage",
        #    value=10,
        #)

        #self.tuition_percentage_discount = Discount.objects.create(
        #    name="10% discount on tuition",
        #    discount_type="general",
        #    value_type="percentage",
        #    value=10,
        #    fee_item=self.tuition_fee_item
        #)
    
    def test_resets_existing_discount(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_tuition_fee_assignment.discount_amount = 500.00
        student_tuition_fee_assignment.net_amount = 3000.00

        student_tuition_fee_assignment.save()

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 0)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 3000)


    def test_one_percentage_fee_item_discount(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        tuition_percentage_discount = Discount.objects.create(
            name="10% discount on tuition",
            discount_type="general",
            value_type="percentage",
            value=10,
            fee_item=tuition_fee_item
        )


        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        StudentDiscount.objects.create(
            student=self.student,
            discount=tuition_percentage_discount,
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 350)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 3150)

    def test_one_fixed_fee_item_discount(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        tuition_fixed_discount = Discount.objects.create(
            name="200 discount on tuition",
            discount_type="general",
            value_type="fixed",
            value=200,
            fee_item=tuition_fee_item
        )


        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        StudentDiscount.objects.create(
            student=self.student,
            discount=tuition_fixed_discount,
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 200)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 3300)

    def test_multiple_fixed_fee_items_discounts(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")
        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        tuition_fixed_discount = Discount.objects.create(
            name="500 discount on tuition",
            discount_type="general",
            value_type="fixed",
            value=500,
            fee_item=tuition_fee_item
        )

        activity_fixed_discount = Discount.objects.create(
            name="100 discount on activity",
            discount_type="general",
            value_type="fixed",
            value=100,
            fee_item=activity_fee_item
        )

        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        activity_grade_fee_item = GradeFeeItem.objects.create(
             fee_item=activity_fee_item,
             grade=self.grade1,
             academic_year=self.academic_year,
             amount=200,
             frequency="yearly",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        StudentDiscount.objects.bulk_create(
            [
                StudentDiscount(
                    student=self.student,
                    discount=tuition_fixed_discount,
                    academic_year=self.academic_year,
                ),
                StudentDiscount(
                    student=self.student,
                    discount=activity_fixed_discount,
                    academic_year=self.academic_year,
                )
            ]
        )

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()
        student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 500)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 3000)

        self.assertEqual(student_activity_fee_assignment.discount_amount, 100)
        self.assertEqual(student_activity_fee_assignment.net_amount, 100)

    def test_multiple_fee_item_percentage_discounts(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")
        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        tuition_percentage_discount = Discount.objects.create(
            name="10% discount on tuition",
            discount_type="general",
            value_type="percentage",
            value=10,
            fee_item=tuition_fee_item
        )

        activity_percentage_discount = Discount.objects.create(
            name="5% discount on activity",
            discount_type="general",
            value_type="percentage",
            value=5,
            fee_item=activity_fee_item
        )

        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        activity_grade_fee_item = GradeFeeItem.objects.create(
             fee_item=activity_fee_item,
             grade=self.grade1,
             academic_year=self.academic_year,
             amount=200,
             frequency="yearly",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        StudentDiscount.objects.bulk_create(
            [
                StudentDiscount(
                    student=self.student,
                    discount=tuition_percentage_discount,
                    academic_year=self.academic_year,
                ),
                StudentDiscount(
                    student=self.student,
                    discount=activity_percentage_discount,
                    academic_year=self.academic_year,
                )
            ]
        )

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()
        student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 350)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 3150)

        self.assertEqual(student_activity_fee_assignment.discount_amount, 10)
        self.assertEqual(student_activity_fee_assignment.net_amount, 190)

    def test_one_fixed_discount_on_gross(self):

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")
        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        fixed_discount_on_gross = Discount.objects.create(
            name="100 discount on total",
            discount_type="general",
            value_type="fixed",
            value=100,
        )

        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=300,
            frequency="per_term",
        )

        activity_grade_fee_item = GradeFeeItem.objects.create(
             fee_item=activity_fee_item,
             grade=self.grade1,
             academic_year=self.academic_year,
             amount=100,
             frequency="yearly",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        StudentDiscount.objects.create(
            student=self.student,
            discount=fixed_discount_on_gross,
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()
        student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 75)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 225)

        self.assertEqual(student_activity_fee_assignment.discount_amount, 25)
        self.assertEqual(student_activity_fee_assignment.net_amount, 75)

    def test_one_percentage_discount_on_gross(self):

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")
        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

        percentage_discount_on_gross = Discount.objects.create(
            name="10% discount on total",
            discount_type="general",
            value_type="percentage",
            value=10,
        )

        tuition_grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=400,
            frequency="per_term",
        )

        activity_grade_fee_item = GradeFeeItem.objects.create(
             fee_item=activity_fee_item,
             grade=self.grade1,
             academic_year=self.academic_year,
             amount=200,
             frequency="yearly",
        )

        student_tuition_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=self.student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        StudentDiscount.objects.create(
            student=self.student,
            discount=percentage_discount_on_gross,
            academic_year=self.academic_year,
        )

        recalculate_student_discounts(self.student, self.academic_year)

        student_tuition_fee_assignment.refresh_from_db()
        student_activity_fee_assignment.refresh_from_db()

        self.assertEqual(student_tuition_fee_assignment.discount_amount, 40)
        self.assertEqual(student_tuition_fee_assignment.net_amount, 360)

        self.assertEqual(student_activity_fee_assignment.discount_amount, 20)
        self.assertEqual(student_activity_fee_assignment.net_amount, 180)
