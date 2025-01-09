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
        self.handle_cache(request.data['email'],
                          'set', serializer.validated_data)

        return Response({'status': 'created'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='update')
    def update_user(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        new_email = request.data.get('new_email', None)
        if not (email and new_email):
            return Response({"error": f"Current email: {email}\nNew email: {new_email}"}, status=status.HTTP_400_BAD_REQUEST)

        self.handle_cache(email, 'set', request.data)

        return Response({'status': 'email updated'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_user(self, request, *args, **kwargs):
        email = get_email_or_400(request)
        user_data = self.handle_cache(email, 'get')
        if not (email == user_data['email']):
            return Response({'error': 'Cached email not equal got'}, status=status.HTTP_400_BAD_REQUEST)
        if user_data:
            self.handle_cache(email, 'delete')

            user = get_user_model().objects.filter(email=email)
            if user.exists():
                user = user[0]
                user.is_registered = True
                user.email = user_data['new_email']
                user.save()
                return Response({'status': 'Email update confirmed'}, status=status.HTTP_200_OK)

            self.perform_create(self.get_serializer(data=user_data))
            return Response({'status': 'Creation confirmed'}, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='rollback')
    def rollback_user(self, request, *args, **kwargs):
        email = get_email_or_400(request)
        new_email = request.data.get('new_email', None)
        move = request.data.get('move', None)
        self.handle_cache(email, 'delete')

        if move != 'confirm':
            return Response({'data': 'First commit rolled back'}, status=status.HTTP_200_OK)

        if new_email:
            user_after_update = User.objects.filter(email=new_email)
            if user_after_update:
                user_after_update[0].email = email
                user_after_update[0].save()
                return Response({'data': 'Update confirm rolled back(made email old)'}, status=status.HTTP_200_OK)
            return Response({"data": "Update confirm rolled back"}, status=status.HTTP_200_OK)

        created_user = User.objects.filter(email=email)
        if created_user:
            created_user[0].delete()
            return Response({'data': "Create rolled back(user deleted)"}, status=status.HTTP_200_OK)
        return Response({"data": "Create rolled back"}, status=status.HTTP_200_OK)
