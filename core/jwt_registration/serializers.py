from rest_framework import serializers
from jwt_registration.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        for attr, value, in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
