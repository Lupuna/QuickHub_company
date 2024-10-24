from rest_framework import serializers
from jwt_registration.serializers import UserSerializer
from company.models import Company, Position, Project, ProjectPosition
from jwt_registration.models import User


class CompanySerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Company
        fields = ('id', 'title', 'description', 'users')

    def create(self, validated_data):
        users_data = validated_data.pop('users', [])
        company = Company.objects.create(**validated_data)

        if users_data:
            user_ids = [user_data['email'] for user_data in users_data]
            users = User.objects.filter(email__in=user_ids)
            company.users.set(users)
        return company

    def update(self, instance, validated_data):
        users_data = validated_data.pop('users', [])
        for attr, value, in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if users_data:
            user_ids = [user_data['email'] for user_data in users_data]
            users = User.objects.filter(email__in=user_ids)
            instance.users.add(*users)

        return instance


class PositionSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        users_data = validated_data.pop('users', [])
        position = Position.objects.create(**validated_data)

        if users_data:
            user_ids = [user_data['email'] for user_data in users_data]
            users = User.objects.filter(email__in=user_ids)
            position.users.set(users)
        return position

    def update(self, instance, validated_data):
        users_data = validated_data.pop('users', [])
        for attr, value, in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if users_data:
            user_ids = [user_data['email'] for user_data in users_data]
            users = User.objects.filter(email__in=user_ids)
            instance.users.add(*users)

        return instance


class ProjectPositionSerializer(serializers.ModelSerializer):
    access_weight = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPosition
        fields = ('id', 'access_weight')
        read_only_fields = ('id',)

    def get_access_weight(self, obj):
        return obj.get_project_access_weight_display()


class PositionForProjectSerializer(serializers.ModelSerializer):
    access_weight = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('id', 'title', 'access_weight')
        read_only_fields = ('id', 'title', 'access_weight')

    def get_access_weight(self, obj):
        return obj.get_access_weight_display()


class ProjectSerializer(serializers.ModelSerializer):
    positions = serializers.SerializerMethodField(read_only=True)
    project_positions = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'company', 'title', 'description', 'positions', 'project_positions')

    def get_positions(self, obj):
        positions_project = obj.positions.all()
        return PositionForProjectSerializer(positions_project, many=True).data

    def get_project_positions(self, obj):
        positions_project = obj.position_projects.all()
        return ProjectPositionSerializer(positions_project, many=True).data


class ProjectPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'company', 'title', 'description')