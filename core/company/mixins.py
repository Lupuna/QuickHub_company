from jwt_registration.models import User


class UserHandlingMixin:

    def create(self, validated_data):
        is_remove = validated_data.pop('is_remove', False)
        users_data = validated_data.pop('users', [])
        instance = super().create(validated_data)
        self._set_users(instance, users_data, is_remove=is_remove)
        return instance

    def update(self, instance, validated_data):
        is_remove = validated_data.pop('is_remove', False)
        users_data = validated_data.pop('users', [])
        instance = super().update(instance, validated_data)
        self._set_users(instance, users_data, created=False, is_remove=is_remove)
        return instance

    @staticmethod
    def _set_users(instance, users_data: list, is_remove=False, created=True):
        if isinstance(users_data, list) and users_data:
            user_emails = [user_data['email'] for user_data in users_data]
            users = User.objects.filter(email__in=user_emails)

            if created:
                instance.users.set(users)
            else:
                if is_remove:
                    instance.users.remove(*users)
                else:
                    existing_users = set(instance.users.all())
                    new_users = set(users)
                    instance.users.add(*(new_users - existing_users))