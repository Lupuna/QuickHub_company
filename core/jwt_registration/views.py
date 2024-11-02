from rest_framework.viewsets import ModelViewSet
from jwt_registration.models import User
from drf_spectacular.utils import extend_schema

from jwt_registration.serializers import UserSerializer


@extend_schema(
    tags=["Create users"]
    )
class RegistrationAPIViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

