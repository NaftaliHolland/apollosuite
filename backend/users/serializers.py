from core.models import School
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, StudentProfile


class UserSerializer(serializers.ModelSerializer):

    # TODO: Add nested serializer for role
    # TODO: Add nested serializer for schools
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'schools',
            'email',
            'phone_number',
            'status',
            'created_at',
        ]

        read_only_fields = ['user_id', 'created_at']


#class StudentProfileSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = StudentProfile
#        fields = [
#            'user',
#            'grade',
#            'stream',
#            'enrollment_date',
#            'admission_number',
#            'assessment_number',
#            'created_at',
#            'updated_at',
#        ]
#
#        read_only_fields = ['created_at', 'updated_at', 'user']

class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    user = UserSerializer()
    school_id = serializers.IntegerField(write_only=True, required=True, 
                                         help_text="School ID for generating admission number")
    
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'user', 'grade', 'stream', 'enrollment_date', 'transfered_from',
            'admission_number', 'assessment_number', 'enrollment_status',
            'created_at', 'updated_at', 'school_id', 'grade_name', 'stream_name'
        ]
        read_only_fields = ['admission_number', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create student profile with auto-generated admission number"""
        user_data = validated_data.pop('user')
        school_id = validated_data.pop('school_id')
        
        # Get the school instance
        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            raise serializers.ValidationError({"school_id": "School not found"})
        
        # Create the user
        user = CustomUser.objects.create(**user_data)
        
        # Add school to user's schools
        user.schools.add(school)
        
        # Create student profile with school parameter
        student_profile = StudentProfile(user=user, **validated_data)
        student_profile.save(school=school)
        
        return student_profile
    
    def update(self, instance, validated_data):
        """Update student profile"""
        # Remove nested user data and school_id if present
        user_data = validated_data.pop('user', None)
        validated_data.pop('school_id', None)  # Don't allow changing school on update
        
        # Update user if user_data is provided
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Update student profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class StudentProfileListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    student_name = serializers.SerializerMethodField()
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'user', 'student_name', 'admission_number', 'grade', 'grade_name',
            'stream', 'stream_name', 'enrollment_status', 'enrollment_date'
        ]
    
    def get_student_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class RegisterSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)

    class Meta:
        model = CustomUser

        fields = [
            'first_name',
            'last_name',
            'password',
            'email',
            'phone_number',
            'schools',
            'student_profile',
        ]

        read_only_fields = ['user_id', 'created_at']

    def create(self, validated_data):
        student_data = validated_data.pop('student_data', None)

        with transaction.atomic():
            user = CustomUser.objects.create_user(**validated_data)

            if student_data:
                StudentProfile.objects.create(user=user, **student_data)


            return user

#class StudentProfileSerializer(serializers.ModelSerializer):
#    # Handle nesting these serializers properly
#
#    class Meta:
#        model = StudentProfile
#        fields = [
#            'user'
#            '
#        ]
