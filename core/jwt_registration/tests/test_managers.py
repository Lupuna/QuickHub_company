from django.test import TestCase
from django.contrib.auth import get_user_model


class TestUserModelTestCase(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.data = {
            'email': 'test_email@gmail.com',
            'password': 'test_password123'
        }
        self.superuser_data = {
            'email': 'admin_email@gmail.com',
            'password': 'admin_password123'
        }
        self.user_data_without_password = {
            'email': 'nopass_email@gmail.com',
        }

        self.superuser_data_without_password = {
            'email': 'nopass_email@gmail.com',
        }

        self.data_with_empty_email = {
            'email': '',
        }

    def test_create_user_success(self):
        user = self.user_model.objects.create_user(**self.data)
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertFalse(user.is_staff)

    def test_create_superuser_success(self):
        superuser = self.user_model.objects.create_superuser(**self.superuser_data)
        self.assertEqual(superuser.email, self.superuser_data['email'])
        self.assertTrue(superuser.check_password(self.superuser_data['password']))
        self.assertTrue(superuser.is_staff)

    def test_superuser_must_be_staff(self):
        with self.assertRaises(ValueError):
            self.user_model.objects.create_superuser(
                email='admin_no_staff@gmail.com',
                password='admin_password123',
                is_staff=False
            )

    def test_create_user_without_password(self):
        user = self.user_model.objects.create_user(**self.user_data_without_password)
        self.assertEqual(user.email, self.user_data_without_password['email'])
        self.assertFalse(user.has_usable_password())

    def test_create_user_without_email(self):
        with self.subTest('test_without_email_field'):
            with self.assertRaises(ValueError):
                self.user_model.objects.create_user(**self.data_with_empty_email)

    def test_create_superuser_without_password(self):
        with self.assertRaises(ValueError):
            self.user_model.objects.create_superuser(**self.superuser_data_without_password)
