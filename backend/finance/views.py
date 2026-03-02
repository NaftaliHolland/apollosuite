from core.permissions import IsMemberOfSchool
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from finance.services import (assign_grade_fee_item_to_students,
                              recalculate_student_discounts, record_payment)

from .models import (Discount, FeeItem, GradeFeeItem, Payment, PaymentItem,
                     StudentDiscount)
from .serializers import (DiscountCreateSerializer, DiscountSerializer,
                          FeeItemCreateSerializer, FeeItemSerializer,
                          GradeFeeItemSerializer, PaymentCreateSerializer,
                          PaymentSerializer, StudentDiscountCreateSerializer,
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


class PaymentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]

        return Payment.objects.for_school(school_id=school_id).all()

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer 

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Payment cannot be modified"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Payments cannot be deleted"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        school = data["school"]

        payments = record_payment(
            student=data["student"],
            amount=data["amount"],
            payment_method=data["payment_method"],
            received_by=request.user,
            term=data["term"],
            academic_year=school.current_academic_year,
            allocations=data["allocations"],
            reference=data["reference"],
            note=data["note"]
        )

        return Response(
            PaymentSerializer(payments, many=True).data,
            status=status.HTTP_201_CREATED
        )
