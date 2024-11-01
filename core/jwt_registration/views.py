from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from jwt_registration.models import User
from drf_spectacular.utils import extend_schema

from jwt_registration.serializers import UserSerializer


@extend_schema(
    tags=["Create users"]
    )
class RegistrationAPIViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

