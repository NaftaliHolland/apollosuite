from django.test import TestCase
from core.models import School, Term, Grade
from finance.models import (
    FeeItem,
    GradeFeeItem,
    Discount,
    StudentDiscount,
    StudentFeeAssignment,
    Payment,
    PaymentItem
)
from django.utils import timezone
