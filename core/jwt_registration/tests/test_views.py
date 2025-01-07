from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from unittest.mock import MagicMock, patch

from jwt_registration.models import User
from jwt_registration.views import RegistrationAPIViewSet
from django.conf import settings


class RegistrationAPIViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.data = {
            'email': 'test_email@gmail.com'
        }
        self.view = RegistrationAPIViewSet()

    def test_get_cache_key(self):
        correct_meaning = settings.USER_TWO_COMMITS_CACHE_KEY.format(
            email=self.data['email'])
        self.assertEqual(self.view.get_cache_key(
            self.data['email']), correct_meaning)

    def test_handle_cache_set(self):
        cache_key = self.view.get_cache_key(self.data['email'])
        self.assertIsNone(cache.get(cache_key))
        self.view.handle_cache(
            email=self.data['email'],
            action='set',
            data=self.data
        )
        self.assertTrue(cache.get(cache_key) is not None)
        cache.delete(cache_key)

    def test_handle_cache_get(self):
        cache_key = self.view.get_cache_key(self.data['email'])
        cache.set(cache_key, self.data, 5*5)
        self.view.handle_cache(self.data['email'], action='get')
        self.assertTrue(cache.get(cache_key) is not None)
        cache.delete(cache_key)

    def test_handle_cache_delete(self):
        cache_key = self.view.get_cache_key(self.data['email'])
        cache.set(cache_key, self.data, 5 * 5)
        self.view.handle_cache(self.data['email'], action='delete')
        self.assertIsNone(cache.get(cache_key))

    def test_handle_cache_with_invalid_action(self):
        with self.assertRaises(ValueError):
            self.view.handle_cache('test', action='invalid')

    def test_create_user(self):
        url = reverse('user-create-user')
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'created'})
        cache_key = self.view.get_cache_key(self.data['email'])
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_create_rollback(self):
        data = self.data
        data.update({'move': 'create'})
        url = reverse('user-rollback-user')

        response_create = self.client.post(
            reverse('user-create-user'), data=self.data)

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        cached_data = cache.get(self.view.get_cache_key(data['email']))
        self.assertIsNone(cached_data)

    def test_update_user(self):
        url = reverse('user-update-user')
        data = self.data
        data.update({'new_email': 'new@gmail.com'})
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'email updated'})
        cache_key = self.view.get_cache_key(self.data['email'])
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_rollback_update(self):
        data = self.data
        data.update({'new_email': 'new@gmail.com', 'move': 'create'})
        url = reverse('user-rollback-user')

        response_update = self.client.post(
            reverse('user-update-user'), data=self.data)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        cached_data = cache.get(self.view.get_cache_key(data['email']))
        self.assertIsNone(cached_data)

    def test_rollback_confirm_create(self):
        data = {**self.data, **{'move': 'confirm'}}

        create_url = reverse('user-create-user')
        first_commit_response = self.client.post(create_url, self.data)
        self.assertIsNotNone(cache.get(self.view.get_cache_key(data['email'])))
        self.assertFalse(bool(User.objects.filter(email=data['email'])))

        confirm_url = reverse('user-confirm-user')
        second_commit = self.client.post(confirm_url, data)
        self.assertIsNone(cache.get(self.view.get_cache_key(data['email'])))
        self.assertTrue(bool(User.objects.filter(email=data['email'])))

        rollback_url = reverse('user-rollback-user')
        rollback_response = self.client.post(rollback_url, data)
        self.assertEqual(rollback_response.status_code, 200)
        self.assertFalse(bool(User.objects.filter(email=data['email'])))

    def test_rollback_confirm_update(self):
        user = User.objects.create(email='test_email@gmail.com')
        data_update = {**self.data, **{'new_email': 'new@gmail.com'}}
        data_rollback = {**data_update, **{'move': 'confirm'}}
        cache

        update_url = reverse('user-update-user')
        first_commit_response = self.client.post(update_url, data_update)
        self.assertIsNotNone(
            cache.get(self.view.get_cache_key(data_update['email'])))
        self.assertFalse(
            bool(User.objects.filter(email=data_update['new_email'])))
        self.assertTrue(bool(User.objects.filter(email=data_update['email'])))

        confirm_url = reverse('user-confirm-user')
        second_commit = self.client.post(confirm_url, data_update)
        self.assertIsNone(
            cache.get(self.view.get_cache_key(data_update['email'])))
        self.assertFalse(bool(User.objects.filter(email=data_update['email'])))
        self.assertTrue(bool(User.objects.filter(
            email=data_update['new_email'])))

        rollback_url = reverse('user-rollback-user')
        rollback_response = self.client.post(rollback_url, data_rollback)
        self.assertEqual(rollback_response.status_code, 200)
        self.assertEqual(User.objects.get(
            email=data_update['email']).email, 'test_email@gmail.com')
