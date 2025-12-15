from rest_framework import routers

from .views import SchoolViewSet

router = routers.SimpleRouter()
router.register(r'schools', SchoolViewSet, basename='school')

urlpatterns = router.urls
