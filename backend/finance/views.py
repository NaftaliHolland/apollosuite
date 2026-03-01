from core.permissions import IsMemberOfSchool
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from finance.services import (assign_grade_fee_item_to_students,
                              recalculate_student_discounts)

from .models import Discount, FeeItem, GradeFeeItem, StudentDiscount
from .serializers import (DiscountCreateSerializer, DiscountSerializer,
                          FeeItemCreateSerializer, FeeItemSerializer,
                          GradeFeeItemSerializer,
                          StudentDiscountCreateSerializer,
                          StudentDiscountSerializer)

# I think I'll have everything accessed from the school url


class FeeItemViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]

        return FeeItem.objects.for_school(school_id=school_id).all()

    def get_serializer_class(self):
        if self.action == "list":
            return FeeItemSerializer
        elif self.action == "retrieve":
            return FeeItemSerializer
        else:
            return FeeItemCreateSerializer


class GradeFeeItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfSchool]
    serializer_class = GradeFeeItemSerializer

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]

        return GradeFeeItem.objects.filter(grade__school_id=school_id)

    def perform_create(self, serializer):

        grade_fee_item = serializer.save()

        assign_grade_fee_item_to_students(grade_fee_item)

class DiscountViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]

        return Discount.objects.for_school(school_id=school_id).all()

    def get_serializer_class(self):
        if self.action == "list":
            return DiscountSerializer
        elif self.action == "retrieve":
            return DiscountSerializer
        else:
            return DiscountCreateSerializer


class StudentDiscountViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]

        # Just get the school
        # school = School.objects.get(pk=school_id)

        return StudentDiscount.objects.filter(discount__school_id=school_id)

    def get_serializer_class(self):
        if self.action == "list":
            return StudentDiscountSerializer
        elif self.action == "retrieve":
            return StudentDiscountSerializer
        else:
            return StudentDiscountCreateSerializer

    def perform_create(self, serializer):
        student_discount = serializer.save()

        student = student_discount.student
        academic_year = student_discount.academic_year

        recalculate_student_discounts(student=student, academic_year=academic_year)
