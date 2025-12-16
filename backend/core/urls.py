# from rest_framework import routers

from django.urls import include, path
from rest_framework_nested import routers

from .views import (AcademicYearViewSet, GradeViewSet, SchoolViewSet,
                    StreamViewSet, TermViewSet)

router = routers.SimpleRouter()
router.register(r"schools", SchoolViewSet, basename="school")

schools_router = routers.NestedSimpleRouter(router, r"schools", lookup="school")
schools_router.register(r"grades", GradeViewSet, basename="grade")
schools_router.register(r"streams", StreamViewSet, basename="stream")
schools_router.register(
    r"academic-years", AcademicYearViewSet, basename="academic-year"
)
schools_router.register(r"terms", TermViewSet, basename="term")

academic_years_router = routers.NestedSimpleRouter(
    schools_router,
    r"academic-years",
    lookup="academic_year"
)

academic_years_router.register(
    r"terms",
    TermViewSet,
    basename="term"
)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(schools_router.urls)),
    path(r"", include(academic_years_router.urls)),
]
