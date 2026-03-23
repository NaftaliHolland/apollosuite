from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import AcademicYear, Grade, School, Stream, Term
from .permissions import IsMemberOfSchool
from .serializers import (AcademicYearListSerializer, AcademicYearSerializer,
                          GradeListSerializer, GradeSerializer,
                          SchoolCreateSerializer, SchoolSerializer,
                          StreamSerializer, TermSerializer)


class SchoolViewSet(viewsets.ModelViewSet):
    #serializer_class = SchoolSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return School.objects.all()

        return School.objects.filter(users=user)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsMemberOfSchool()]


    def get_serializer_class(self):
        if self.action == "list":
            # TODO: Need to add a School list serializer
            return SchoolSerializer
        elif self.action == "retrieve":
            return SchoolSerializer
        else:
            return SchoolCreateSerializer


class GradeViewSet(viewsets.ModelViewSet):

    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        user = self.request.user

        school_id = self.kwargs["school_pk"]
        return Grade.objects.filter(
            school_id=school_id,
        )

    def get_serializer_class(self):
        if self.action == "list":
            return GradeListSerializer

        return super().get_serializer_class()

class StreamViewSet(viewsets.ModelViewSet):
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]
        return Stream.objects.filter(
            school_id=school_id,
        )

class AcademicYearViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]
        return AcademicYear.objects.filter(
            school_id=school_id,
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AcademicYearListSerializer

        return super().get_serializer_class()

class TermViewSet(viewsets.ModelViewSet):
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]
        academic_year_id = self.kwargs.get("academic_year_pk")

        if academic_year_id:
            return Term.objects.filter(
                academic_year=academic_year_id
            )

        return Term.objects.filter(
            academic_year__school_id=school_id,
        )
