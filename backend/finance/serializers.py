from core.models import AcademicYear, Grade, Term
from core.serializers import CurrentAcademicYearDefault, CurrentSchoolDefault
from rest_framework import serializers
from users.models import StudentProfile

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

class TermAmountSerializer(serializers.Serializer):
    term = serializers.PrimaryKeyRelatedField(queryset=Term.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class GradeFeeItemPerTermSerializer(serializers.Serializer):
    academic_year = serializers.CharField(default=CurrentAcademicYearDefault())
    #academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    fee_item = serializers.PrimaryKeyRelatedField(queryset=FeeItem.objects.all())
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all())
    terms = TermAmountSerializer(many=True)

class GradeFeeItemSerializer(serializers.ModelSerializer):
    academic_year = serializers.CharField(default=CurrentAcademicYearDefault())

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
    class Meta:
        model = Payment
        fields = [
            'school',
            'id',
            'student',
            'amount',
            'payment_method',
            'reference',
            'received_by',
            'received_at',
            'term',
            'academic_year',
            'note',
            'created_at',
        ]

class PaymentItemInputSerializer(serializers.Serializer):
    fee_assignment_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1, max_value=10000000)


class PaymentCreateSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    school = serializers.CharField(default=CurrentSchoolDefault())
    term = serializers.PrimaryKeyRelatedField(queryset=Term.objects.all())
    #academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())
    reference = serializers.CharField(required=False, allow_blank=True, default='')
    note = serializers.CharField(required=False, allow_blank=True, default='')
    allocations = PaymentItemInputSerializer(many=True)


    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greate than 0.")

        return value
    
    def validate_allocations(self, value):
        if not value:
            raise serializers.ValidationError("At least one validation is required")

        return value

    # TODO: Implement this
    #def validate(self, data):
    #    pass


class PaymentItemSerializser(serializers.ModelSerializer):
    pass

class FeeSummarySerializer(serializers.ModelSerializer):
    pass
