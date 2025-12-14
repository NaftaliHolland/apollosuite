from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    # TODO: Add nested serializer for role
    # TODO: Add RoleSerializer
    # TODO: Add nested serializer for school
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'school',
            'email',
            'phone_number',
            'roles',
            'status',
            'created_at',
        ]

        read_only_fields = ['user_id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = [
            'first_name',
            'last_name',
            'password',
            'email',
            'phone_number',
            'school',
            'roles',
        ]

        read_only_fields = ['user_id', 'created_at']

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            school=validated_data.get("school"),
            email=validated_data["email"],
            roles=validated_data["roles"],
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
        )
