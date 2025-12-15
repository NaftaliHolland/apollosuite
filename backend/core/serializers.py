from rest_framework import serializers

from .models import School

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
