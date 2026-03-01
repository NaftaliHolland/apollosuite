from core.permissions import IsMemberOfSchool
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from finance.services import assign_fees_to_student

from .models import CustomUser, StudentProfile
from .serializers import (RegisterSerializer, StudentProfileCreateSerializer,
                          StudentProfileListSerializer,
                          StudentProfileSerializer, UserSerializer)


class RegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User created successfully",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        user = authenticate(phone_number=phone_number, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
        )


class StudentProfileViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        permissions = [IsAuthenticated()]

        school_id = self.kwargs.get("school_pk") or self.kwargs.get("school_id")

        if school_id:
            permissions.append(IsMemberOfSchool())

        return permissions

    def get_serializer_class(self):
        if self.action == "list":
            return StudentProfileListSerializer
        elif self.action in ["retrieve", "partial_update", "update"]:
            return StudentProfileSerializer
        else:
            return StudentProfileCreateSerializer

        return StudentProfileSerializer

    def get_queryset(self):
        """
        Optionally filter students by school.
        Use query parameter: ?school_id=1
        """
        school_id = self.kwargs.get("school_pk") or self.kwargs.get("school_id")

        user = self.request.user

        if self.action in ["retrieve", "partial_update", "update"] or user.is_staff:
            return StudentProfile.objects.all()

        return StudentProfile.objects.for_school(school_id)

    def perform_update(self, serializer):
        student = serializer.save()
        data = self.request.data
        academic_year = student.school.current_academic_year

        if data.get('grade'):
            assign_fees_to_student(student, academic_year)
