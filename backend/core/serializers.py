from rest_framework import serializers

from .models import Grade, School

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

class GradeSerializer(serializers.ModelSerializer):
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
