from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from jwt_registration.models import User
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
from django.conf import settings

from jwt_registration.serializers import UserSerializer


@extend_schema(
    tags=["Create user"]
)
class RegistrationAPIViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], url_path='create')
    def create_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cache_key = settings.USER_TWO_COMMITS_CACHE_KEY.format(email=request.data['email'])
        cache.set(cache_key, serializer.validated_data, settings.CACHE_LIFE_TIME)

        return Response({'status': 'created'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_user(self, request, *args, **kwargs):
        user_email = request.data.get('email')
        if not user_email:
            return Response({'error': 'User creation not initiated'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = settings.USER_TWO_COMMITS_CACHE_KEY.format(email=request.data['email'])
        user_data = cache.get(cache_key)
        if user_data:
            self.perform_create(self.get_serializer(data=user_data))
            cache.delete(cache_key)
            return Response({'status': 'confirmed'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='rollback')
    def rollback_user(self, request, *args, **kwargs):
        user_email = request.data.get('email')
        if not user_email:
            return Response({'error': 'User creation not initiated'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = settings.USER_TWO_COMMITS_CACHE_KEY.format(email=request.data['email'])
        user_data = cache.get(cache_key)
        if user_data:
            cache.delete(cache_key)
        user = User.objects.filter(email=user_email)
        if user.exists(): user.delete()
        return Response({'status': 'rolled back'}, status=status.HTTP_200_OK)
