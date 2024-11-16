from rest_framework import serializers
from jwt_registration.serializers import UserSerializer
from company.models import Company, Position, Project, Department
from company.mixins import UserHandlingMixin


class CompanySerializer(UserHandlingMixin, serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Company
        fields = ('id', 'title', 'users')


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
        fields = ('id', 'company', 'title', 'description', 'positions', 'users')

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
        fields = ('id', 'title', 'description', 'parent', 'users')


class UserInCompanyValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()