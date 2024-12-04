from jwt_registration.models import User


class UserHandlingMixin:

    def create(self, validated_data):
        users_data = validated_data.pop('users', [])
        instance = super().create(validated_data)
        self._set_users(instance, users_data)
        return instance

    def update(self, instance, validated_data):
        users_data = validated_data.pop('users', [])
        instance = super().update(instance, validated_data)
        self._set_users(instance, users_data, created=False)
        return instance

    @staticmethod
    def _set_users(instance, users_data, created=True):
        if isinstance(users_data, list) and users_data:
            user_emails = [user_data['email'] for user_data in users_data]
            users = User.objects.filter(email__in=user_emails)
            if created:
                instance.users.set(users)
            else:
                instance.users.add(*users)
