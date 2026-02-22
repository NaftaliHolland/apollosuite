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


def recalculate_student_discounts(student, academic_year):
    # TODO:
    # - Fetches all StudentDiscount for that student in that particular academic_year
    # - resets StudentFeeAssignment.discount to 0
    # - for student_discount in student_discounts:
    #   - if student_discount.discount.fee_item is not null then we apply that to that particular fee item in the StudentFeeAssignment 
    student_fee_assignments = StudentFeeAssignment.objects.filter(
        student=student,
        academic_year=academic_year,
    ).update(discount_amount=0)

    if not student_fee_assignments:
        return

    student_discounts = StudentDiscount.objects.filter(
        student=student,
        academic_year=academic_year,
    )


    # For first pass
    fee_item_specific_discounts = student_discounts.exclude(discount__fee_item__isnull=True).all()

    for student_discount in fee_item_specific_discounts:
        discount = student_discount.discount

        # Get all matching assignments
        fee_item = discount.fee_item
        student_fee_item_assignment = StudentFeeAssignment.objects.get(
            student=student,
            grade_fee_item__fee_item=fee_item
        )

        discount_value = discount.value
        discount_value_type = discount.value_type

        fee_assignment_gross = student_fee_item_assignment.gross_amount

        discount = 0

        if discount_value_type == "percentage":
            # get the percentage of that particular fee item
            discount = (discount_value / 100) * fee_assignment_gross
        elif discount_value_type == "fixed":
            discount = fee_assignment_gross - discount_value

        student_fee_item_assignment.discount_amount += discount

        student_fee_item_assignment.save()

    # For second pass
    general_discounts = student_discounts.filter(discount__fee_item=None).all()


    for student_discount in student_discounts:
        discount = student_discount.discount

        if student_discount.discount.fee_item:
            # Get the StudentFeeAssignment related to that fee item
            fee_item = discount.fee_item
            student_fee_item_assignment = StudentFeeAssignment.objects.get(
                student=student,
                grade_fee_item__fee_item=fee_item
            )

            discount_value = discount.value
            discount_value_type = discount.value_type

            fee_assignment_gross = student_fee_item_assignment.gross_amount

            discount = 0

            if discount_value_type == "percentage":
                # get the percentage of that particular fee item
                discount = (discount_value / 100) * fee_assignment_gross
            elif discount_value_type == "fixed":
                discount = fee_assignment_gross - discount_value

            student_fee_item_assignment.discount_amount += discount

            student_fee_item_assignment.save()

        else:


            # apply on total
                # Just do the math

            # Get gross
            # Calculate discount
            # Calculate net
            
            # I need to check if it is a percentage and calculate that
            # If it is fixed and also calculate that



def assign_grade_fee_item_to_students(grade_fee_item):
    pass

def record_payment(student, amount, payment_method, received_by, term, academic_year, allocations, reference, note):
    pass

def get_student_fee_summary(student, academic_year, term=None):
    pass

