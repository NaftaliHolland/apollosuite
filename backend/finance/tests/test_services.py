from core.models import AcademicYear, Grade, School, Term
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from finance.models import (
    Discount,
    FeeItem,
    GradeFeeItem,
    Payment,
    PaymentItem,
    StudentDiscount,StudentFeeAssignment
)
from finance.services import (assign_fees_to_student,
                              assign_grade_fee_item_to_students,
                              recalculate_student_discounts, record_payment)
from users.models import AdminProfile, StudentProfile

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
            school=self.school,
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            school=self.school,
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
            school=self.school,
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            school=self.school,
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
            school=self.school,
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
            school=self.school,
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
            school=self.school,
            name="500 discount on tuition",
            discount_type="general",
            value_type="fixed",
            value=500,
            fee_item=tuition_fee_item
        )

        activity_fixed_discount = Discount.objects.create(
            school=self.school,
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
            school=self.school,
            name="10% discount on tuition",
            discount_type="general",
            value_type="percentage",
            value=10,
            fee_item=tuition_fee_item
        )

        activity_percentage_discount = Discount.objects.create(
            school=self.school,
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
            school=self.school,
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
            school=self.school,
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

class AssignGradeFeeItemToStudentsTest(TestCase):
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
            school=self.school,
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 3",
            order=3,
            start_date=term_3_start_date,
            end_date=term_3_end_date,
        )
        self.grade1 = Grade.objects.create(school=self.school, name="Grade1")

    def test_assigns_fee_item_to_all_students_in_linked_grade(self):

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        student_user2 = User.objects.create_user(
            first_name="Jane",
            last_name="Doe",
            phone_number="0722222342",
            password="unsecurePass123",
        )
        student_2 = StudentProfile.objects.create(
            user=student_user2,
            school=self.school,
            grade=self.grade1
        )

        student_user3 = User.objects.create_user(
            first_name="James",
            last_name="Doe",
            phone_number="0722922342",
            password="unsecurePass123",
        )
        student_3 = StudentProfile.objects.create(
            user=student_user3,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        self.assertEqual(
            StudentFeeAssignment.objects.filter(
                student=student,
                grade_fee_item=grade_fee_item
            ).count(),
            0
        )

        self.assertEqual(
            StudentFeeAssignment.objects.filter(
                student=student_2,
                grade_fee_item=grade_fee_item
            ).count(),
            0
        )

        self.assertEqual(
            StudentFeeAssignment.objects.filter(
                student=student_3,
                grade_fee_item=grade_fee_item
            ).count(),
            0
        )

        assign_grade_fee_item_to_students(grade_fee_item)

        student_1_assignments = StudentFeeAssignment.objects.filter(
            student=student,
            grade_fee_item=grade_fee_item
        )

        student_2_assignments = StudentFeeAssignment.objects.filter(
            student=student_2,
            grade_fee_item=grade_fee_item
        )

        student_3_assignments = StudentFeeAssignment.objects.filter(
            student=student_3,
            grade_fee_item=grade_fee_item
        )

        self.assertEqual(len(student_1_assignments), 3) # For the three terms
        self.assertEqual(len(student_2_assignments), 3) # For the three terms
        self.assertEqual(len(student_3_assignments), 3) # For the three terms


    def test_does_nothing_if_no_students_in_grade(self):
        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        assign_grade_fee_item_to_students(grade_fee_item)


        self.assertEqual(
            StudentFeeAssignment.objects.filter(
                grade_fee_item=grade_fee_item
            ).count(),
            0
        )


    def does_not_duplicate_assignments_when_called_more_than_once_with_the_same_grade_fee_item(self):
        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        student_user2 = User.objects.create_user(
            first_name="Jane",
            last_name="Doe",
            phone_number="0722222342",
            password="unsecurePass123",
        )
        student_2 = StudentProfile.objects.create(
            user=student_user2,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        grade_fee_item = GradeFeeItem.objects.create(
            fee_item=tuition_fee_item,
            grade=self.grade1,
            academic_year=self.academic_year,
            amount=3500,
            frequency="per_term",
        )

        assign_grade_fee_item_to_students(grade_fee_item)

        student_1_assignments = StudentFeeAssignment.objects.filter(
            student=student,
            grade_fee_item=grade_fee_item
        )

        student_2_assignments = StudentFeeAssignment.objects.filter(
            student=student_2,
            grade_fee_item=grade_fee_item
        )

        self.assertEqual(len(student_1_assignments), 3) # For the three terms
        self.assertEqual(len(student_2_assignments), 3) # For the three terms

        assign_grade_fee_item_to_students(grade_fee_item)

        self.assertEqual(len(student_1_assignments), 3) # For the three terms
        self.assertEqual(len(student_2_assignments), 3) # For the three terms


class RecordPaymentTests(TestCase):
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
            school=self.school,
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 3",
            order=3,
            start_date=term_3_start_date,
            end_date=term_3_end_date,
        )
        self.grade1 = Grade.objects.create(school=self.school, name="Grade1")

    def test_raises_error_when_allocation_sum_does_not_equal_amount(self):
        admin_user = User.objects.create_user(
            first_name="Admin",
            last_name="Doe",
            phone_number="0798282343",
            password="unsecurePass123",
        )

        admin = AdminProfile.objects.create(
            user=admin_user,
        )

        admin.schools.add(self.school)

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        allocations = [
            {
                "fee_assignment_id": 1,
                "amount": 200,
            },
            {
                "fee_assignment_id": 1,
                "amount": 900,
            },
            {
                "fee_assignment_id": 1,
                "amount": 200,
            },
        ]


        with self.assertRaises(ValidationError):
            record_payment(
                student=student,
                amount=5000,
                payment_method="M-pesa",
                received_by=admin_user,
                term=self.term1,
                academic_year=self.academic_year,
                allocations=allocations,
                reference="KKLSKDJF",
                note="Some random note"
            )

    def test_creates_one_payment_item_per_allocation(self):
        admin_user = User.objects.create_user(
            first_name="Admin",
            last_name="Doe",
            phone_number="0798282343",
            password="unsecurePass123",
        )

        admin = AdminProfile.objects.create(
            user=admin_user,
        )

        admin.schools.add(self.school)

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

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
            student=student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )


        allocations = [
            {
                "fee_assignment_id": 1,
                "amount": 200,
            },
            {
                "fee_assignment_id": 2,
                "amount": 900,
            },
        ]

        payments = record_payment(
            student=student,
            amount=1100,
            payment_method="M-pesa",
            received_by=admin_user,
            term=self.term1,
            academic_year=self.academic_year,
            allocations=allocations,
            reference="KKLSKDJF",
            note="Some random note"
        )

        self.assertEqual(
            len(payments),
            2
        )

    def test_associated_payment_items_created(self):
        admin_user = User.objects.create_user(
            first_name="Admin",
            last_name="Doe",
            phone_number="0798282343",
            password="unsecurePass123",
        )

        admin = AdminProfile.objects.create(
            user=admin_user,
        )

        admin.schools.add(self.school)

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

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
            student=student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        allocations = [
            {
                "fee_assignment_id": 1,
                "amount": 200,
            },
            {
                "fee_assignment_id": 2,
                "amount": 100,
            },
        ]

        payments = record_payment(
            student=student,
            amount=300,
            payment_method="M-pesa",
            received_by=admin_user,
            term=self.term1,
            academic_year=self.academic_year,
            allocations=allocations,
            reference="KKLSKDJF",
            note="Some random note"
        )

        self.assertEqual(
            PaymentItem.objects.all().count(),
            2
        )

    def test_payment_items_have_the_right_amount(self):
        admin_user = User.objects.create_user(
            first_name="Admin",
            last_name="Doe",
            phone_number="0798282343",
            password="unsecurePass123",
        )

        admin = AdminProfile.objects.create(
            user=admin_user,
        )

        admin.schools.add(self.school)

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

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
            student=student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        allocations = [
            {
                "fee_assignment_id": 1,
                "amount": 300,
            },
            {
                "fee_assignment_id": 2,
                "amount": 100,
            },
        ]

        payments = record_payment(
            student=student,
            amount=400,
            payment_method="M-pesa",
            received_by=admin_user,
            term=self.term1,
            academic_year=self.academic_year,
            allocations=allocations,
            reference="KKLSKDJF",
            note="Some random note"
        )


        first_payment_item = PaymentItem.objects.get(pk=1)
        second_payment_item = PaymentItem.objects.get(pk=2)

        self.assertEqual(first_payment_item.amount, 300)
        self.assertEqual(second_payment_item.amount, 100)

    def test_raises_error_when_allocation_amount_is_zero_or_negative(self):
        pass

    def test_raises_error_when_single_allocation_exceeds_outstanding_balance(self):
        admin_user = User.objects.create_user(
            first_name="Admin",
            last_name="Doe",
            phone_number="0798282343",
            password="unsecurePass123",
        )

        admin = AdminProfile.objects.create(
            user=admin_user,
        )

        admin.schools.add(self.school)

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

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
            student=student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        allocations = [
            {
                "fee_assignment_id": 1,
                "amount": 300,
            },
            {
                "fee_assignment_id": 2,
                "amount": 100,
            },
        ]

        payments = record_payment(
            student=student,
            amount=400,
            payment_method="M-pesa",
            received_by=admin_user,
            term=self.term1,
            academic_year=self.academic_year,
            allocations=allocations,
            reference="KKLSKDJF",
            note="Some random note"
        )


        first_payment_item = PaymentItem.objects.get(pk=1)
        second_payment_item = PaymentItem.objects.get(pk=2)

        self.assertEqual(first_payment_item.amount, 300)
        self.assertEqual(second_payment_item.amount, 100)


    def test_payment_items_have_correct_allocated_amounts(self):
        pass

    def test_returns_payment_with_prefetched_items(self):
        pass

    def test_each_allocation_does_not_exceed_current_balance(self):
        pass

    def test_all_student_fee_assignments_are_updated_with_correct_values(self):
        pass

    def test_payment_instances_are_created_with_right_values(self):
        pass


class TestStudentFeeAssignment(TestCase):
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
            school=self.school,
            academic_year=self.academic_year,
            name="Term 1",
            order=1,
            start_date=term_1_start_date,
            end_date=term_1_end_date,
        )
        self.term2 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 2",
            order=2,
            start_date=term_2_start_date,
            end_date=term_2_end_date,
        )
        self.term3 = Term.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            name="Term 3",
            order=3,
            start_date=term_3_start_date,
            end_date=term_3_end_date,
        )
        self.grade1 = Grade.objects.create(school=self.school, name="Grade1")

    def test_correct_balance(self):
        admin_user = User.objects.create_user(
            first_name="Admin",
            last_name="Doe",
            phone_number="0798282343",
            password="unsecurePass123",
        )

        admin = AdminProfile.objects.create(
            user=admin_user,
        )

        admin.schools.add(self.school)

        student_user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            phone_number="0711111111",
            password="unsecurePass123",
        )
        student = StudentProfile.objects.create(
            user=student_user,
            school=self.school,
            grade=self.grade1
        )

        tuition_fee_item = FeeItem.objects.create(school=self.school, name="Tuition")

        activity_fee_item = FeeItem.objects.create(school=self.school, name="Activity")

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
            student=student,
            grade_fee_item=tuition_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=tuition_grade_fee_item.amount,
            discount_amount=0,
            net_amount=tuition_grade_fee_item.amount,
        )

        student_activity_fee_assignment = StudentFeeAssignment.objects.create(
            student=student,
            grade_fee_item=activity_grade_fee_item,
            term=self.term1,
            academic_year=self.academic_year,
            gross_amount=activity_grade_fee_item.amount,
            discount_amount=0,
            net_amount=activity_grade_fee_item.amount,
        )

        allocations = [
            {
                "fee_assignment_id": 1,
                "amount": 200,
            },
            {
                "fee_assignment_id": 2,
                "amount": 50,
            },
        ]

        payments = record_payment(
            student=student,
            amount=250,
            payment_method="M-pesa",
            received_by=admin_user,
            term=self.term1,
            academic_year=self.academic_year,
            allocations=allocations,
            reference="KKLSKDJF",
            note="Some random note"
        )

        # Make a payment

        self.assertEqual(student_tuition_fee_assignment.balance, 200)
        self.assertEqual(student_activity_fee_assignment.balance, 150)
