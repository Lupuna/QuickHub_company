from rest_framework import serializers
from jwt_registration.models import User
from company.serializers import CompanyForUserSerializer
from company.serializers import PositionNoUsersSerializer, DepartmentNoUsersSerializer


class OnlyUserEmailSerializer(serializers.ModelSerializer):
    positions = PositionNoUsersSerializer(many=True)
    departments = DepartmentNoUsersSerializer(many=True)

    class Meta:
        model = User
        fields = ('email', 'positions', 'departments')


class UserCompanySerializer(serializers.ModelSerializer):
    companies = CompanyForUserSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'companies')


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
