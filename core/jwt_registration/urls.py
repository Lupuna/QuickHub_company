from django.urls import path, include
from rest_framework.routers import SimpleRouter
from jwt_registration.views import RegistrationAPIViewSet


router = SimpleRouter()
router.register(r'users', RegistrationAPIViewSet)

urlpatterns = [
    path('api/v1', include(router.urls)),
]
