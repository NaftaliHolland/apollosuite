from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Grade, School
from .serializers import GradeSerializer, SchoolSerializer


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

    # NOTE: If I do this one more time then I probably need a custom permission

    serializer_class = GradeSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Grade.objects.all()

        school_id = self.kwargs["school_pk"]
        return Grade.objects.filter(school_id=school_id)

    def perform_create(self, serializer):
        school_id = self.kwargs["school_pk"]
        serializer.save(school_id=school_id)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        return [IsAuthenticated()]
