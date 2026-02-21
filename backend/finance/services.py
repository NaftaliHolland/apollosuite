from django.core.exceptions import ObjectDoesNotExist

from finance.models import (Discount, FeeItem, GradeFeeItem, Payment,
                            PaymentItem, StudentDiscount, StudentFeeAssignment)


def assign_fees_to_student(student, academic_year):
    """
    Triggered when:
        - a new student is enrolled
        - a new GradeFeeItem is created (FeeItem added to class)
    """

    #TODO:
    # - Get all grade_fee_items for the student's class for the given academic year.
    # - for each:
    #   - if frequency == 'per_term' create a StudentFeeAssignement for each term in the academic year
    #   - if frequency == 'yearly', create one only for the first term - order == 1
    #   - if frequencey == 'once', create one but with term set as null
    # If one already exists skip - write a test for this
    # calls recalcultate_student_discounts to apply existing discounts

    grade = student.grade
    terms = academic_year.terms.all()

    # TODO: make this query a bit more efficient
    grade_fee_items = GradeFeeItem.objects.filter(grade=grade, academic_year=academic_year).all()

    assignments = []


    for grade_fee_item in grade_fee_items:
        if grade_fee_item.frequency == "per_term":
            for term in terms:
                assignment, _ = StudentFeeAssignment.objects.get_or_create(
                    student=student,
                    grade_fee_item=grade_fee_item,
                    term=term,
                    defaults={
                        "gross_amount": grade_fee_item.amount,
                        "net_amount": grade_fee_item.amount,
                        "academic_year": academic_year
                    }
                )

                assignments.append(assignment)

        elif grade_fee_item.frequency == "yearly":
            first_term = academic_year.terms.all().first()
            assignment, _= StudentFeeAssignment.objects.get_or_create(
                student=student,
                grade_fee_item=grade_fee_item,
                term=first_term,
                defaults={
                    "gross_amount": grade_fee_item.amount,
                    "net_amount": grade_fee_item.amount,
                    "academic_year": academic_year
                }
            )

            assignments.append(assignment)

        elif grade_fee_item.frequency == "one_time":
            assignment, _ = StudentFeeAssignment.objects.get_or_create(
                student=student,
                grade_fee_item=grade_fee_item,
                term=None,
                defaults={
                    "gross_amount": grade_fee_item.amount,
                    "net_amount": grade_fee_item.amount,
                    "academic_year": academic_year
                }
            )

            assignments.append(assignment)

        # TODO: apply discounts

    return assignments


def recalculate_student_discounts(studnet, academic_year):
    pass


def assign_grade_fee_item_to_students(grade_fee_item):
    pass

def record_payment(student, amount, payment_method, received_by, term, academic_year, allocations, reference, note):
    pass

def get_student_fee_summary(student, academic_year, term=None):
    pass

