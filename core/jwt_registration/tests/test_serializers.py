from django.test import TestCase
from jwt_registration.models import User
from jwt_registration.serializers import UserSerializer


class UserSerializerTestCase(TestCase):

    def setUp(self):
        self.valid_data_1 = {
            'email': 'test1@example.com',
        }

        self.valid_data_2 = {
            'email': 'test2@example.com',
        }

        self.new_data = {
            'email': 'new_email@example.com',
        }

        self.user = User.objects.create_user(**self.valid_data_1)

    def test_create_user(self):
        serializer = UserSerializer(data=self.valid_data_2)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, self.valid_data_2['email'])

    def test_create_user_invalid_email(self):
        invalid_data = self.valid_data_2.copy()
        invalid_data['email'] = ''
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_update_user(self):
        serializer = UserSerializer(instance=self.user, data=self.new_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        self.assertEqual(updated_user.email, self.new_data['email'])

    def test_update_user_invalid_email(self):
        new_data = {
            'email': ''
        }
        serializer = UserSerializer(instance=self.user, data=new_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)