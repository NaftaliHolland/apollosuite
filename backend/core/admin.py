from django.contrib import admin

from .models import MapLocation, School

admin.site.register(School)
admin.site.register(MapLocation)
