from django.urls import path, include
from rest_framework.routers import SimpleRouter
from jwt_registration.views import RegistrationAPIViewSet


user_router = SimpleRouter()
user_router.register(r'users', RegistrationAPIViewSet)

urlpatterns = [
    path('', include(user_router.urls)),
]
