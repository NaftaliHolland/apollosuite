from core.models import AcademicYear, Grade, School, Term
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from users.models import TenantManager

User = get_user_model()

class FeeItem(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    objects = TenantManager()

    def __str__(self):
        return self.name


# TODO: Add is_active field to Academic year

class GradeFeeItem(models.Model):
    """
    Defines how much a grade pays for a given fee item and the frequency of the payment
    """
    FEE_FREQUENCY_CHOICES = [
        ('per_term', 'Per Term'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]
    fee_item = models.ForeignKey(FeeItem, on_delete=models.PROTECT, related_name="classes")
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name="class_fee_items")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="class_fee_items")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(choices=FEE_FREQUENCY_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['academic_year', 'fee_item', 'grade'], name="unique_grade_fee_item")
        ]

    def __str__(self):
        return f"{self.grade} - {self.fee_item} ({self.get_frequency_display()})"

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('sibling', 'Sibling'),
        ('general', 'General'),
        ('scholarship', 'Scholarship'),
    ]

    VALUE_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="discounts")
    name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    # IF fee_item is set, discount applies to this fee item only. If null it applies to total
    fee_item = models.ForeignKey(
        FeeItem,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='discounts',
    )
    is_active = models.BooleanField(default=True)

    objects = TenantManager()
    

    def clean(self):
        if self.value_type == 'percentage' and self.value > 100:
            raise ValidationError("Percentage discount cannot exceed 100%.")

    def __str__(self):
        return f"{self.name} ({self.get_discount_type_display()})"

class StudentDiscount(models.Model):
    student = models.ForeignKey('users.StudentProfile', on_delete=models.PROTECT, related_name="discounts")
    discount = models.ForeignKey(Discount, on_delete=models.PROTECT, related_name='student_discounts')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='student_discounts')
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    objects = TenantManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'discount', 'academic_year'], name="unique_student_discount")
        ]

    def __str__(self):
        return f"{self.student} - {self.discount}"

class StudentFeeAssignment(models.Model):
    student = models.ForeignKey("users.StudentProfile", on_delete=models.PROTECT, related_name="fee_assignments")
    grade_fee_item = models.ForeignKey(GradeFeeItem, on_delete=models.PROTECT, related_name="assigments")
    # term set to NULL if the items frequency is ONCE e.g admission.
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fee_assignments"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="fee_assignments")
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'grade_fee_item', 'term'], name="unique_student_fee_assignment")
        ]

    @property
    def amount_paid(self):
        return sum(item.amount for item in self.payment_items.all())

    @property
    def balance(self):
        return self.net_amount - self.amount_paid

    @property
    def is_fully_paid(self):
        return self.balance <= 0

    def __str__(self):
        return f"{self.student} - {self.grade_fee_item.fee_item} | {self.term or self.academic_year}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
    ]

    student = models.ForeignKey('users.StudentProfile', on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(max_length=255, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payments_received')
    received_at = models.DateTimeField(auto_now_add=True)
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="payments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="payments")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def amount_allocated(self):
        return sum(item.amount for item in self.items.all())

    @property
    def unallocated_amount(self):
        return self.amount - self.amount_allocated

    def __str__(self):
        return f"Payment #{self.pk} - {self.student} - {self.amount}"


class PaymentItem(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="items")
    fee_assignment = models.ForeignKey(StudentFeeAssignment, on_delete=models.PROTECT, related_name="payment_items")
    amount = models.DecimalField(max_digits=10, decimal_places=2)


    def clean(self):
        if self.amount > self.fee_assignment.balance:
            raise ValidationError(
                f"Amount exceeds outstanding balance of {self.fee_assignment.balance} "
                f" for {self.fee_assignment.grade_fee_item.fee_item}."
            )

        def __str__(self):
            return f"{self.payment} -> {self.fee_assignment.grade_fee_item.fee_item} ({self.amount})"
