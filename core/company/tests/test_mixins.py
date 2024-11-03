from unittest.mock import MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from company.mixins import UserHandlingMixin


class UserHandlingMixinTests(TestCase):
    def setUp(self):
        user = get_user_model()
        self.user1 = user.objects.create(email='user1@example.com')
        self.user2 = user.objects.create(email='user2@example.com')
        self.user3 = user.objects.create(email='user3@example.com')
        self.instance = MagicMock()
        self.instance.users = MagicMock()
        self.user_data = [{'email': self.user2.email}, {'email': self.user3.email}]

    def test_set_users_create(self):
        mixin = UserHandlingMixin()
        mixin._set_users(self.instance, self.user_data, created=True)
        self.instance.users.set.assert_called_once()
        called_args = list(self.instance.users.set.call_args[0][0])
        expected_users = [self.user2, self.user3]
        self.assertEqual(called_args, expected_users)

    def test_set_users_update(self):
        mixin = UserHandlingMixin()
        mixin._set_users(self.instance, self.user_data, created=False)
        self.instance.users.add.assert_called_once()
        called_args = self.instance.users.add.call_args[0][0]
        self.assertEqual(called_args, self.user2)
