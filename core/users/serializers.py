from rest_framework import serializers
from jwt_registration.models import User
from company.serializers import CompanyForUserSerializer


class OnlyUserEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', )


class UserCompanySerializer(serializers.ModelSerializer):
    companies = CompanyForUserSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'companies')


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()