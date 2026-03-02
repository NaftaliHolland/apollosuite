from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from services.assign_admin_to_school import assign_admin_to_school

from .models import AcademicYear, Grade, School, Stream, Term

# TODO: Check these nested relationships later not now I don't have time

class SchoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'year_started',
            'about',
            'website',
            'address',
            'map_location',
            'contact_email',
            'contact_phone',
            'logo_url',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user

        validated_data["created_by"] = user
        
        school = super().create(validated_data)

        assign_admin_to_school(user, school)
        
        return school
        
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'year_started',
            'about',
            'website',
            'address',
            'map_location',
            'created_by',
            'contact_email',
            'contact_phone',
            'logo_url',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]

class CurrentSchoolDefault:
    requires_context = True

    def __call__(self, serializer_field):
        view = serializer_field.context['view']
        school = School.objects.get(pk=view.kwargs['school_pk'])
        return school

class GradeSerializer(serializers.ModelSerializer):
    school = serializers.HiddenField(default=CurrentSchoolDefault())

    class Meta:
        model = Grade
        fields = [
            'id',
            'name',
            'school',
            'description',
            'streams',
            'grade_teachers',
            'grade_representatives',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'id',
            'school',
            'created_at',
        ]

        def validate_name(self, value):
            return value.replace(' ', '').lower()

        validators = [
            UniqueTogetherValidator(
                queryset=Grade.objects.all(),
                fields=['school', 'name'],
                message='A grade with a similar name already exists',
            )
        ]

    # NOTE: I should be validating not mutatin stuff here what is wrong with me

    def validate_name(self, value):
        return  value.replace(' ', '').lower()

class StreamSerializer(serializers.ModelSerializer):
    school = serializers.HiddenField(default=CurrentSchoolDefault())

    class Meta:
        model = Stream
        fields = [
            'id',
            'name',
            'school',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'school',
            'created_at',
        ]

        validators = [
            UniqueTogetherValidator(
                queryset=Stream.objects.all(),
                fields=['school', 'name'],
                message='A stream with a similar name already exists',
            )
        ]

    def validate_name(self, value):
        return  value.replace(' ', '').lower()


class AcademicYearSerializer(serializers.ModelSerializer):
    school = serializers.HiddenField(default=CurrentSchoolDefault())

    class Meta:
        model = AcademicYear
        fields = [
            'id',
            'school',
            'name',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]


        validators = [
            UniqueTogetherValidator(
                queryset=AcademicYear.objects.all(),
                fields=['school', 'name'],
                message='An academic year with a similar name already exists',
            )
        ]

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "start_date must be before end_date"
            )

        return attrs

    def validate_name(self, value):
        return  value.replace(' ', '').lower()

class CurrentAcademicYearDefault:
    requires_context = True

    def __call__(self, serializer_field):
        view = serializer_field.context['view']
        academic_year = AcademicYear.objects.get(pk=view.kwargs['academic_year_pk'])
        return academic_year

class TermSerializer(serializers.ModelSerializer):
    school = serializers.HiddenField(default=CurrentSchoolDefault())
    academic_year = serializers.HiddenField(default=CurrentAcademicYearDefault())

    class Meta:
        model = Term
        fields = [
            'id',
            'school',
            'academic_year',
            'name',
            'order',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'academic_year',
            'created_at',
        ]
