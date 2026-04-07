from core.permissions import IsMemberOfSchool
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from finance.services import (assign_grade_fee_item_to_students,
                              create_grade_fee_items_per_term,
                              recalculate_student_discounts, record_payment)

from .models import (Discount, FeeItem, GradeFeeItem, Payment, PaymentItem,
                     StudentDiscount)
from .serializers import (DiscountCreateSerializer, DiscountSerializer,
                          FeeItemCreateSerializer, FeeItemSerializer,
                          GradeFeeItemPerTermSerializer,
                          GradeFeeItemSerializer, PaymentCreateSerializer,
                          PaymentSerializer, StudentDiscountCreateSerializer,
                          StudentDiscountSerializer)


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

    def get_serializer_class(self):

        if self.request.data.get("frequency", None) == "per_term":
            return GradeFeeItemPerTermSerializer

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.data.get("frequency") == "per_term":

            validated_data = serializer.validated_data
            validated_data["frequency"] = "per_term"

            instances = create_grade_fee_items_per_term(validated_data)

            output_serializer = GradeFeeItemSerializer(instances, many=True)

            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        else:
            grade_fee_item = serializer.save()

            grade = serializer.validated_data.get("grade")
            academic_year =serializer.validated_data.get("academic_year")

            assign_grade_fee_item_to_students(grade, academic_year)

            return Response(serializer.data, status=status.HTTP_201_CREATED)



        return super().create(request, *args, **kwargs)

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
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Payments cannot be deleted"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
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
            note=data["note"],
        )

        return Response(
            PaymentSerializer(payments, many=True).data, status=status.HTTP_201_CREATED
        )
