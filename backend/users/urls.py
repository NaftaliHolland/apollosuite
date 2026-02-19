from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import LoginAPIView, RegisterAPIView, StudentProfileViewSet

router = DefaultRouter()
router.register(r'students', StudentProfileViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
]
