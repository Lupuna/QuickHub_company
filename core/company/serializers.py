from rest_framework import serializers
from jwt_registration.serializers import UserSerializer
from company.models import Company, Position, Project, Department
from company.mixins import UserHandlingMixin


class CompanySerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Company
        fields = ('id', 'title', 'users', 'description')


class CompanyForUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'title')


class PositionSerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)
    access_weight = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = (
            'id', 'title', 'description',
            'access_weight', 'company', 'users'
        )

    def get_access_weight(self, obj):
        return obj.get_access_weight_display()


class PositionNoUsersSerializer(PositionSerializer):

    class Meta:
        model = Position
        fields = (
            'id', 'title', 'description',
            'access_weight', 'company'
        )


class PositionNoModelSerializer(serializers.Serializer):
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


class ProjectSerializer(UserHandlingMixin, serializers.ModelSerializer):
    positions = serializers.SerializerMethodField(read_only=True)
    users = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'company', 'title',
                  'description', 'positions', 'users')

    def get_positions(self, obj):
        positions_project = obj.positions.all()
        return PositionForProjectSerializer(positions_project, many=True).data


class ProjectPostSerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'company', 'title', 'description', 'users')


class DepartmentSerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Department
        fields = ('id', 'title', 'description', 'parent', 'users', 'color')


class DepartmentNoUsersSerializer(DepartmentSerializer):

    class Meta:
        model = Department
        fields = ('id', 'title', 'description', 'parent', 'company', 'color')


class DepartmentNoModelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    parent = serializers.IntegerField()
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    color = serializers.CharField()


class LinkNoModelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    link = serializers.CharField()


class ProfileUserForDepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    image_identifier = serializers.CharField()
    date_joined = serializers.CharField()
    links = LinkNoModelSerializer(many=True)
    positions = PositionNoModelSerializer(many=True)
