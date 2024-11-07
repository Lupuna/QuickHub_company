from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from jwt_registration.models import User
from drf_spectacular.utils import extend_schema

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
        self.perform_create(serializer)

        return Response({'status': 'created'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_user(self, request, *args, **kwargs):
        user_email = request.data.get('email')

        if not user_email:
            return Response({'error': 'User creation not initiated'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = User.objects.get(email=user_email)
                user.is_active = True
                user.save()
            return Response({'status': 'confirmed'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='rollback')
    def rollback_user(self, request, *args, **kwargs):
        user_email = request.data.get('email')

        if not user_email:
            return Response({'error': 'User creation not initiated'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.get(email=user_email).delete()
            return Response({'status': 'rolled back'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
