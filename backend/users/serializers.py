from core.models import School
from core.serializers import CurrentSchoolDefault
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from utils.generate_admission_number import generate_admission_number
from utils.generate_fake_phone import generate_fake_phone

from .models import PROFILE_ROLES, CustomUser, ParentProfile, StudentProfile


class UserSerializer(serializers.ModelSerializer):

    active_role = serializers.SerializerMethodField()
    schools = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "status",
            "active_role",
            "roles",
            "schools",
        ]

        read_only_fields = ["user_id", "created_at"]

    def get_active_role(self, obj):
        roles_dict = {k: v for k, v in PROFILE_ROLES}
        active_role = obj.active_role

        return roles_dict[active_role]

    def get_schools(self, obj):
    # TODO: get all schools
        if hasattr(obj, "adminprofile"):
            return [school.id for school in obj.adminprofile.schools.all()]
        elif hasattr(obj, "parentprofile"):
            return [school.id for school in obj.parentprofile.schools.all()]
        elif hasattr(obj, "studentprofile"):
            return [obj.studentprofile.school.id]
        elif hasattr(obj, "staffprofile"):
            return [school.id for school in obj.staffprofile.schools.all()]

class StudentProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    school = serializers.HiddenField(default=CurrentSchoolDefault())
    parent_first_name = serializers.CharField(required=False, write_only=True)
    parent_last_name = serializers.CharField(required=False, write_only=True)
    parent_phone_number = serializers.CharField(required=False, write_only=True)
    parent_email = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "first_name",
            "last_name",
            "parent_first_name",
            "parent_last_name",
            "parent_phone_number",
            "parent_email",
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
        ]
        read_only_fields = [
            "id",
            "admission_number",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):

        school = validated_data.get("school")

        user_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
        }

        parent_data = {
            "first_name": validated_data.pop("parent_first_name"),
            "last_name": validated_data.pop("parent_last_name"),
            "phone_number": validated_data.pop("parent_phone_number"),
            "email": validated_data.pop("parent_email"),
        }

        phone_number = generate_fake_phone()
        # TODO: generate_admisison_number
        admission_number = generate_admission_number(school)

        student_user = CustomUser.objects.create_user(
            **user_data,
            phone_number=phone_number,
        )

        validated_data["admission_number"] = admission_number

        student_profile = StudentProfile(user=student_user, **validated_data)
        student_profile.save()

        parent_user = CustomUser.objects.get_or_create_user(
            **parent_data
        )

        parent, _ = ParentProfile.objects.get_or_create(user=parent_user)
        parent.schools.add(school)
        parent.children.add(student_user)
        parent.save()

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

class ParentProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParentProfile
        fields = [

        ]

        read_only_fields = [
        ]



class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    # TODO: Handle nested objects

    class Meta:
        model = StudentProfile
        fields = [
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
        ]

class StudentProfileListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""

    #use_id = serializers.PrimaryKeyRelatedField()
    student_name = serializers.SerializerMethodField()
    grade_name = serializers.CharField(source="grade.name", read_only=True, default="")
    stream_name = serializers.CharField(source="stream.name", read_only=True, default="")

    class Meta:
        model = StudentProfile
        fields = [
            "user_id",
            "student_name",
            "admission_number",
            "assessment_number",
            "grade_name",
            "stream_name",
            "enrollment_status",
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
