from core.models import School
from core.serializers import CurrentSchoolDefault
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from utils.generate_fake_phone import generate_fake_phone

from .models import CustomUser, StudentProfile


class UserSerializer(serializers.ModelSerializer):

    # TODO: Add nested serializer for role
    # TODO: Add nested serializer for schools

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            #"schools",
            "email",
            "phone_number",
            "status",
            "created_at",
        ]

        read_only_fields = ["user_id", "created_at"]



class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    school = serializers.HiddenField(default=CurrentSchoolDefault())

    #user = UserSerializer()
    #school_id = serializers.IntegerField(
    #    write_only=True,
    #    required=True,
    #    help_text="School ID for generating admission number",
    #)

    #grade_name = serializers.CharField(source="grade.name", read_only=True)
    #stream_name = serializers.CharField(source="stream.name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            #"user",
            "first_name",
            "last_name",
            "school",
            "grade",
            "stream",
            "enrollment_date",
            "transfered_from",
            "admission_number",
            "assessment_number",
            "enrollment_status",
            "enrollment_date",
            "created_at",
            "updated_at",
            #"school_id",
        ]
        read_only_fields = [
            "id",
            "admission_number",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create student profile with auto-generated admission number"""

        user_data = validated_data.pop("user")
        #first_name = validated_data.pop("first_name")
        #last_name = validated_data.pop("last_name")

        phone_number = generate_fake_phone()
        # TODO: generate fake phone

        user = CustomUser.objects.create_user(
            **user_data,
            phone_number=phone_number
        )

        student_profile = StudentProfile(user=user, **validated_data)
        student_profile.save()

        return student_profile

    def update(self, instance, validated_data):
        """Update student profile"""
        user_data = validated_data.pop("user", None)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class StudentProfileListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""

    student_name = serializers.SerializerMethodField()
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    stream_name = serializers.CharField(source="stream.name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "user",
            "student_name",
            "admission_number",
            "grade",
            "grade_name",
            "stream",
            "stream_name",
            "enrollment_status",
            "enrollment_date",
        ]

    def get_student_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class RegisterSerializer(serializers.ModelSerializer):
    #student_profile = StudentProfileSerializer(required=False)
    #phone_number = serializers.CharField(required=False)

    class Meta:
        model = CustomUser

        fields = [
            "first_name",
            "last_name",
            "password",
            "email",
            "phone_number",
            #"schools",
            #"student_profile",
        ]

        read_only_fields = ["user_id", "created_at"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    #def create(self, validated_data):
        #student_data = validated_data.pop("student_data", None)

        #with transaction.atomic():
            #user = CustomUser.objects.create_user(**validated_data)

            #if student_data:
                #StudentProfile.objects.create(user=user, **student_data)

            #return user
