from core.models import School
from core.permissions import IsMemberOfSchool
from django.contrib.auth import authenticate, get_user_model
from finance.services import assign_fees_to_student, get_student_fee_summary
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import PROFILE_ROLES, StudentProfile
from .serializers import (RegisterSerializer, StudentProfileCreateSerializer,
                          StudentProfileListSerializer,
                          StudentProfileSerializer, StudentSummarySerializer,
                          UserSerializer)

User = get_user_model()

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
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

class ProfileAPIView(APIView):
    permissions = [IsAuthenticated]

    def get(self, request):
        user = self.request.user

        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user

        role = request.data.get("role")

        if not role:
            return Response(
                {"details": "Missing role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        roles_dict = {k: v for v, k in PROFILE_ROLES}

        valid_roles = user.roles

        if role not in valid_roles:
            return Response(
                {"details": "User does not have this role" },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.active_role = roles_dict[role]

        user.save(update_fields=["active_role"])

        return Response(
            {"active_role": role}
        )

class UserViewSet(viewsets.ModelViewSet):


    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)

        return Response(serializer.data)

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
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "roles": user.roles,
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
            if self.request.query_params.get("type", None) == "summary":
                return StudentSummarySerializer

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
            return StudentProfile.objects.select_related("user")

        return StudentProfile.objects.for_school(school_id)

    def perform_update(self, serializer):
        student = serializer.save()
        data = self.request.data
        academic_year = student.school.current_academic_year

        if data.get('grade'):
            assign_fees_to_student(student, academic_year)

    @action(detail=True, methods=["get"], url_path="fee-summary")
    def fee_summary(self, request, pk=None, *args, **kwargs):
        student = self.get_object()

        school_id = self.kwargs.get("school_pk") or self.kwargs.get("school_id")
        school = School.objects.get(pk=school_id)
        academic_year = school.current_academic_year

        fee_summary = get_student_fee_summary(student, academic_year)

        return Response(fee_summary)
