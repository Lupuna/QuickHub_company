from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

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
        correct_meaning = settings.USER_TWO_COMMITS_CACHE_KEY.format(email=self.data['email'])
        self.assertEqual(self.view.get_cache_key(self.data['email']), correct_meaning)

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

    def test_confirm_user(self):
        self.view.handle_cache(self.data['email'], 'set', self.data)
        url = reverse('user-confirm-user')
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'confirmed'})
        cache_key = self.view.get_cache_key(self.data['email'])
        self.assertIsNone(cache.get(cache_key))

    def test_confirm_user_already_exists(self):
        User.objects.create(email=self.data['email'])
        self.view.handle_cache(self.data['email'], 'set', self.data)
        url = reverse('user-confirm-user')
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'already_confirmed'})
        cache_key = self.view.get_cache_key(self.data['email'])
        self.assertIsNone(cache.get(cache_key))

    def test_rollback_user(self):
        self.view.handle_cache(self.data['email'], 'set', self.data)
        url = reverse('user-rollback-user')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'rolled back'})
        cache_key = self.view.get_cache_key(self.data['email'])
        self.assertIsNone(cache.get(cache_key))
        user = User.objects.filter(email=self.data['email'])
        self.assertFalse(user.exists())
