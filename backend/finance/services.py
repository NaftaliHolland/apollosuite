from core.models import Term
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Sum
from users.models import StudentProfile

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

    recalculate_student_discounts(student, academic_year)

    return assignments


@transaction.atomic
def recalculate_student_discounts(student, academic_year):

    # TODO: Create submissions and bulk update once, remove all those unnecessary saves


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

    ## Trying to build all this in one pass is not easy
    ## Now this is development, I like this, I am not an LLM
    ## For first pass

    # TODO: Optimize these queries dude

    fee_item_specific_discounts = student_discounts.exclude(discount__fee_item__isnull=True).all()

    for student_discount in fee_item_specific_discounts:
        discount = student_discount.discount

        # Get all matching assignments
        fee_item = discount.fee_item

        # I already made a query to get all these when I was setting everything to 0
        # Why am I doing this again?? Bad? maybe
        # No that was different, I'm getting one for only that specific fee item, which I know I will get right now

        student_fee_item_assignment = StudentFeeAssignment.objects.get(
            student=student,
            grade_fee_item__fee_item=fee_item
        )

        discount_value = discount.value
        discount_value_type = discount.value_type

        fee_assignment_gross = student_fee_item_assignment.gross_amount

        discount_amount = 0

        if discount_value_type == "percentage":
            discount_amount = (discount_value / 100) * fee_assignment_gross
        elif discount_value_type == "fixed":
            discount_amount = discount_value

        student_fee_item_assignment.discount_amount += discount_amount
        student_fee_item_assignment.net_amount -= discount_amount

        student_fee_item_assignment.save()

    ## For second pass
    general_discounts = student_discounts.filter(discount__fee_item=None)

    student_fee_assignments = StudentFeeAssignment.objects.filter(
        student=student,
        academic_year=academic_year,
    )

    for student_discount in general_discounts:
        discount = student_discount.discount

        discount_value = discount.value
        discount_value_type = discount.value_type

        discount_amount = 0

        total_gross = student_fee_assignments.aggregate(Sum('gross_amount'))["gross_amount__sum"]

        for student_fee_assignment in student_fee_assignments:
            if discount_value_type == "percentage":
                discount_amount = (discount_value / 100) * student_fee_assignment.gross_amount

            elif discount_value_type == "fixed":
                discount_amount = (student_fee_assignment.gross_amount / total_gross) * discount_value

            student_fee_assignment.discount_amount += discount_amount
            student_fee_assignment.net_amount -= discount_amount

            # TODO: I shouldn't be calling save here, check this
            student_fee_assignment.save()

@transaction.atomic
def assign_grade_fee_item_to_students(grade_fee_item):
    """
    Triggered when a new GradeFeeItem is created
    """
    grade = grade_fee_item.grade
    students = grade.students.all()

    if not students:
        return


    school = grade_fee_item.grade.school
    academic_year = grade_fee_item.academic_year

    for student in students:
        assign_fees_to_student(student, academic_year)

    ##NOTE: Only active students????
    #student_fee_assignments = []
    #fee_item_frequency = grade_fee_item.frequency

    #all_terms = list(school.terms.filter(
    #    school=school,
    #    academic_year=academic_year
    #))

    #term_one = all_terms[0]

    #fee_assignment_term = (
    #    None if fee_item_frequency == "one_time"
    #    else term_one if fee_item_frequency == ["yearly"]
    #    else all_terms
    #)

    #for student in students:
    #    if not isinstance(fee_assignment_term, list):
    #        student_fee_assignment = StudentFeeAssignment(
    #            student=student,
    #            grade_fee_item=grade_fee_item,
    #            term = fee_assignment_term,
    #            academic_year=academic_year,
    #            gross_amount=grade_fee_item.amount,
    #            net_amount=grade_fee_item.amount
    #        )
    #        student_fee_assignments.append(student_fee_assignment)

    #    else:
    #        for term in fee_assignment_term:
    #            student_fee_assignment = StudentFeeAssignment(
    #                student=student,
    #                grade_fee_item=grade_fee_item,
    #                term = term,
    #                academic_year=academic_year,
    #                gross_amount=grade_fee_item.amount,
    #                net_amount=grade_fee_item.amount
    #            )

    #            student_fee_assignments.append(student_fee_assignment)

    #StudentFeeAssignment.objects.bulk_create(
    #    student_fee_assignments
    #)

    ## TODO: Not good, there has to be a better way to handle this

    #for student in students:
    #    recalculate_student_discounts(student, academic_year)

@transaction.atomic
def record_payment(
        student,
        amount,
        payment_method,
        received_by,
        term,
        academic_year,
        allocations, # list of dicts [{"fee_assignment_id": int, "amount": Decimal}]
        reference,
        note
):


    allocations_sum = sum(allocation["amount"] for allocation in allocations)

    if allocations_sum != amount:
        raise ValidationError("amount doesn't match allocations total")

    # TODO: What do I need to do here??
    # Check if the sum of all allocations equals the total amount
    # Validates that each allocation does not exceed the current balance of that fee_assignment. Raise ValidationError
    # Creates a Payment record
    # For each allocation create a new PaymentItem, assign that Payment
    # Return the created Payment


    # TODO: get all fee assignments related toa that student in that particular term/year I don't even know at this point

    fee_assignment_ids = [allocation["fee_assignment_id"] for allocation in allocations]

    student_fee_assignments = StudentFeeAssignment.objects.filter(
        id__in=fee_assignment_ids
    )

    payment_objects = []
    payment_item_objects = []

    for allocation in allocations:
        # Create payment instances
        fee_assignment = StudentFeeAssignment.objects.get(pk=allocation["fee_assignment_id"])
        
        # Get balance

        payment = Payment(
            payment_method=payment_method,
            student=student,
            amount=allocation["amount"],
            reference=reference,
            received_by=received_by,
            term=term,
            academic_year=academic_year,
            note=note,
        )
        payment_objects.append(payment)


        payment_item = PaymentItem(
            payment=payment,
            fee_assignment=fee_assignment,
            amount=allocation["amount"]
        )
        payment_item_objects.append(payment_item)

    payments = Payment.objects.bulk_create(
        payment_objects
    )

    PaymentItem.objects.bulk_create(
        payment_item_objects
    )

    return payments

def get_student_fee_summary(student, academic_year, term=None):
    pass
