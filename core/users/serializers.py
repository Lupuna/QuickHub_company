from rest_framework import serializers
from jwt_registration.models import User
from company.serializers import CompanyForUserSerializer


class UserCompanySerializer(serializers.ModelSerializer):
    companies = CompanyForUserSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'companies')
