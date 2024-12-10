from rest_framework import serializers

from company.tasks import notify_users_created
from jwt_registration.models import User
from jwt_registration.serializers import UserSerializer
from company.models import Company, Position, Project, Department
from company.mixins import UserHandlingMixin
from loguru import logger


class CompanySerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)
    is_remove = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = Company
        fields = ('id', 'title', 'users', 'description', 'is_remove')

    @staticmethod
    def _set_users(instance, users_data: list, is_remove=False, created=True):
        if isinstance(users_data, list) and users_data:
            user_emails = [user_data['email'] for user_data in users_data]

            existing_users = User.objects.filter(email__in=user_emails)
            existing_user_emails = set(existing_users.values_list('email', flat=True))
            new_user_emails = set(user_emails) - existing_user_emails
            if new_user_emails:
                User.objects.bulk_create([User(email=email, is_registered=False) for email in new_user_emails])
                notify_users_created.delay(list(new_user_emails))
                existing_users = User.objects.filter(email__in=user_emails)

            if created:
                instance.users.set(existing_users)
            else:
                if is_remove:
                    instance.users.remove(*existing_users)
                else:
                    current_users = set(instance.users.all())
                    users_to_add = set(existing_users) - current_users
                    instance.users.add(*users_to_add)


class CompanyForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'title')


class PositionSerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)
    access_weight = serializers.SerializerMethodField()
    is_remove = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = Position
        fields = (
            'id', 'title', 'description',
            'access_weight', 'company', 'users', 'is_remove'
        )

    def get_access_weight(self, obj):
        return obj.get_access_weight_display()


class ExternalAPIRequestPositionNoUsersSerializer(PositionSerializer):
    class Meta:
        model = Position
        fields = (
            'id', 'title', 'description',
            'access_weight', 'company',
        )


class PositionNoUsersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    access_weight = serializers.CharField()
    company = serializers.IntegerField()


class PositionForProjectSerializer(serializers.ModelSerializer):
    access_weight = serializers.SerializerMethodField()
    project_positions = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('id', 'title', 'access_weight', 'project_positions')
        read_only_fields = ('id', 'title', 'access_weight')

    def get_project_positions(self, obj):
        project_positions = obj.project_positions.all()
        return [position_project.get_project_access_weight_display() for position_project in project_positions]

    def get_access_weight(self, obj):
        return obj.get_access_weight_display()


class DepartmentSerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)
    is_remove = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = Department
        fields = ('id', 'company', 'title', 'description', 'parent', 'users', 'color', 'is_remove')


class DepartmentNoUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'title', 'description', 'parent', 'company', 'color')


class DepartmentTitleIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ('id', 'title')


class ProjectSerializer(UserHandlingMixin, serializers.ModelSerializer):
    positions = serializers.SerializerMethodField(read_only=True)
    is_remove = serializers.BooleanField(required=False, write_only=True, default=False)
    departments = DepartmentTitleIdSerializer(many=True, required=False)
    users = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'company', 'title',
                  'description', 'positions', 'users',
                  'departments', 'color', 'priority',
                  'creation_date', 'date_of_update',
                  'is_remove')

    def get_positions(self, obj):
        positions_project = obj.positions.all()
        return PositionForProjectSerializer(positions_project, many=True).data

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        if 'departments' in data:
            result['departments'] = [
                {'id': department['id']} for department in data['departments']
            ]
        return result

    def update(self, instance, validated_data):
        departments_ids = [department['id'] for department in validated_data.pop('departments', [])]
        departments = Department.objects.filter(id__in=departments_ids)
        instance = super().update(instance, validated_data)
        instance.departments.add(*(set(departments) - set(instance.departments.all())))
        return instance


class ProjectPostSerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)
    is_remove = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = Project
        fields = ('id', 'company', 'title', 'description', 'users', 'is_remove')


class LinkNoModelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    link = serializers.CharField()


class UserInfoNoDepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    otchestwo = serializers.CharField()
    phone = serializers.CharField()
    business_phone = serializers.CharField()
    city = serializers.CharField()
    image_identifier = serializers.CharField()
    date_joined = serializers.CharField()
    links = LinkNoModelSerializer(many=True)
    positions = PositionNoUsersSerializer(many=True)


class DepartmentWithUserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    parent = serializers.IntegerField()
    users = UserInfoNoDepSerializer(many=True)
    color = serializers.CharField()
