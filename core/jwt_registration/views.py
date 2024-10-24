from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from jwt_registration.models import User

from jwt_registration.serializers import UserSerializer


class RegistrationAPIViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

