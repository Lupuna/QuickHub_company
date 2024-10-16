from rest_framework import serializers
from jwt_registration.serializers import UserSerializer
from company.models import Company
from jwt_registration.models import User


class CompanySerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)
    positions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'title', 'description', 'users', 'positions')

    def get_positions(self, obj):
        return [{'id': position.id, 'name': str(position)} for position in obj.positions.all()]

    def create(self, validated_data):
        users_data = validated_data.pop('users', [])
        company = Company.objects.create(**validated_data)

        if users_data:
            user_ids = [user_data['id'] for user_data in users_data]
            users = User.objects.filter(id__in=user_ids)
            company.users.add(*users)
        return company

    def update(self, instance, validated_data):
        users_data = validated_data.pop('users', [])
        for attr, value, in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if users_data:
            user_ids = [user_data['id'] for user_data in users_data]
            users = User.objects.filter(id__in=user_ids)
            instance.users.set(users)

        return instance
