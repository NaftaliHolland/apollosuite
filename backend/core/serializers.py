from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Grade, School, Stream

# TODO: Check these nested relationships later not now I don't have time

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
        # I need to check if school doesn't exisit
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

        validators = [
            UniqueTogetherValidator(
                queryset=Grade.objects.all(),
                fields=['school', 'name'],
                message='A grade with a similar name already exists',
            )
        ]

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
        return value.replace(' ', '').lower()
