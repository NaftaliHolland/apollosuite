#from rest_framework import routers

from django.urls import include, path
from rest_framework_nested import routers

from .views import GradeViewSet, SchoolViewSet

router = routers.SimpleRouter()
router.register(r'schools', SchoolViewSet, basename='school')

schools_router = routers.NestedSimpleRouter(router, r'schools', lookup='school')
schools_router.register(r'grades', GradeViewSet, basename='grade')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(schools_router.urls)),
]
