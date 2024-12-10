from django.contrib.auth import get_user_model
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from jwt_registration.models import User
from jwt_registration.utils import get_email_or_400
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
from django.conf import settings

from jwt_registration.serializers import UserSerializer


@extend_schema(
    tags=["Create user"]
)
class RegistrationAPIViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def handle_cache(self, email, action, data=None):
        cache_key = self.get_cache_key(email)
        match action:
            case 'set' if data is not None:
                cache.set(cache_key, data, settings.CACHE_LIFE_TIME)
            case 'get':
                return cache.get(cache_key)
            case 'delete':
                cache.delete(cache_key)
            case _:
                raise ValueError(f"Invalid cache action: {action}")

    def get_cache_key(self, email):
        return settings.USER_TWO_COMMITS_CACHE_KEY.format(email=email)

    @action(detail=False, methods=['post'], url_path='create')
    def create_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.handle_cache(request.data['email'], 'set', serializer.validated_data)

        return Response({'status': 'created'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_user(self, request, *args, **kwargs):
        email = get_email_or_400(request)

        user_data = self.handle_cache(email, 'get')
        if user_data:
            self.handle_cache(email, 'delete')

            user = get_user_model().objects.filter(email=email)
            if user.exists():
                user[0].is_registered = True
                user[0].save()
                return Response({'status': 'already_confirmed'}, status=status.HTTP_200_OK)
            self.perform_create(self.get_serializer(data=user_data))
            return Response({'status': 'confirmed'}, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='rollback')
    def rollback_user(self, request, *args, **kwargs):
        email = get_email_or_400(request)

        self.handle_cache(email, 'delete')
        user = User.objects.filter(email=email)
        if user.exists(): user.delete()
        return Response({'status': 'rolled back'}, status=status.HTTP_200_OK)
