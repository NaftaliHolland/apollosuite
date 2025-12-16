from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import AcademicYear, Grade, School, Stream, Term
from .permissions import IsMemberOfSchool
from .serializers import (AcademicYearSerializer, GradeSerializer,
                          SchoolSerializer, StreamSerializer, TermSerializer)


class SchoolViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolSerializer


    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return School.objects.all()

        return School.objects.filter(users=user)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        return [IsAuthenticated()]

class GradeViewSet(viewsets.ModelViewSet):

    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        user = self.request.user

        school_id = self.kwargs["school_pk"]
        return Grade.objects.filter(
            school_id=school_id,
            school__users=self.request.user,
        )

class StreamViewSet(viewsets.ModelViewSet):
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]
        return Stream.objects.filter(
            school_id=school_id,
            school__users=self.request.user,
        )

class AcademicYearViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]
        return AcademicYear.objects.filter(
            school_id=school_id,
            school__users=self.request.user,
        )

class TermViewSet(viewsets.ModelViewSet):
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticated, IsMemberOfSchool]

    def get_queryset(self):
        school_id = self.kwargs["school_pk"]
        return Term.objects.filter(
            academic_year__school_id=school_id,
            academic_year__school__users=self.request.user,
        )
