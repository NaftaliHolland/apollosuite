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

from .models import CustomUser, StudentProfile
from .serializers import (
    RegisterSerializer,
    StudentProfileCreateSerializer,
    StudentProfileListSerializer,
    StudentProfileSerializer,
    UserSerializer,
)


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
    """
    ViewSet for managing student profiles.

    list: Get all students
    retrieve: Get a specific student
    create: Create a new student
    update: Update a student (PUT)
    partial_update: Partially update a student (PATCH)
    destroy: Delete a student
    """

    queryset = StudentProfile.objects.select_related("school").all()

    # serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_serializer_class(self):
        if self.action == "list":
            return StudentProfileListSerializer
        elif self.action == "retrieve":
            return StudentProfileSerializer
        else:
            return StudentProfileCreateSerializer

        return StudentProfileSerializer

    def get_queryset(self):
        """
        Optionally filter students by school.
        Use query parameter: ?school_id=1
        """
        queryset = super().get_queryset()
        school_id = self.request.query_params.get("school_id")

        if school_id:
            queryset = queryset.filter(school_id=school_id)

        return queryset.distinct()
