from django.contrib import admin

from .models import (
    AcademicYear,
    MapLocation,
    School,
    Term,
    Stream,
    Grade,
)

admin.site.register(School)
admin.site.register(MapLocation)
admin.site.register(AcademicYear)
admin.site.register(Term)
admin.site.register(Grade)
admin.site.register(Stream)
