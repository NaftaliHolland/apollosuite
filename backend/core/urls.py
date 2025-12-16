#from rest_framework import routers

from django.urls import include, path
from rest_framework_nested import routers

from .views import GradeViewSet, SchoolViewSet, StreamViewSet

router = routers.SimpleRouter()
router.register(r'schools', SchoolViewSet, basename='school')

schools_router = routers.NestedSimpleRouter(router, r'schools', lookup='school')
schools_router.register(r'grades', GradeViewSet, basename='grade')
schools_router.register(r'streams', StreamViewSet, basename='stream')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(schools_router.urls)),
]
