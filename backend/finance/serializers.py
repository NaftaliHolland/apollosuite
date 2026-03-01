from core.serializers import CurrentSchoolDefault
from rest_framework import serializers

from .models import (Discount, FeeItem, GradeFeeItem, Payment, PaymentItem,
                     StudentDiscount, StudentFeeAssignment)


class FeeItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeeItem
        fields = [
            'id',
            'school',
            'name',
            'description',
            'is_active',
        ]
        read_only_fields = ['id']

class FeeItemCreateSerializer(serializers.ModelSerializer):
    school = serializers.CharField(default=CurrentSchoolDefault())

    class Meta:
        model = FeeItem
        fields = [
            'id',
            'school',
            'name',
            'description',
            'is_active',
        ]
        read_only_fields = ['id']

class GradeFeeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeFeeItem
        fields = [
            'id',
            'fee_item',
            'grade',
            'academic_year',
            'amount',
            'frequency',
        ]

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            "id",
            "school",
            "name",
            "discount_type",
            "value_type",
            "value",
            "fee_item",
        ]

class DiscountCreateSerializer(serializers.ModelSerializer):
    school = serializers.CharField(default=CurrentSchoolDefault())

    class Meta:
        model = Discount
        fields = [
            "id",
            "school",
            "name",
            "discount_type",
            "value_type",
            "value",
            "fee_item",
        ]

class StudentDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDiscount
        fields = [
            "id",
            "student",
            "discount",
            "academic_year",
            "assigned_by"
        ]

class StudentDiscountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDiscount
        fields = [
            "id",
            "student",
            "discount",
            "academic_year",
            "assigned_by"
        ]

    def create(self, validated_data):
        user = self.context["request"].user

        validated_data["assigned_by"] = user

        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    pass

class PaymentItemSerializser(serializers.ModelSerializer):
    pass
