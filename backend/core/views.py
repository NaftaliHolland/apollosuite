from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import School
from .serializers import SchoolSerializer


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
