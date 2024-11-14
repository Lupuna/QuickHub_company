from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework.routers import SimpleRouter

from jwt_registration.views import RegistrationAPIViewSet


class RegistrationAPIRouterTestCase(TestCase):

    def test_registration_list_route(self):
        url = reverse('user-list')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, RegistrationAPIViewSet)

    def test_registration_detail_route(self):
        url = reverse('user-detail', args=[1])
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, RegistrationAPIViewSet)

    def test_registration_create_route(self):
        url = reverse('user-create-user')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, RegistrationAPIViewSet)

    def test_registration_confirm_route(self):
        url = reverse('user-confirm-user')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, RegistrationAPIViewSet)

    def test_registration_rollback_route(self):
        url = reverse('user-rollback-user')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, RegistrationAPIViewSet)