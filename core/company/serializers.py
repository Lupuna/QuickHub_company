from rest_framework import serializers
from jwt_registration.serializers import UserSerializer
from company.models import Company
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
