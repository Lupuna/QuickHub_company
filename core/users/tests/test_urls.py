from django.test import TestCase
from django.urls import reverse, resolve
from users.views import UserCompanyAPIViewSet


class UserCompanyAPIRouterTestCase(TestCase):

    def test_user_company_list_route(self):
        url = reverse('user-company-list')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, UserCompanyAPIViewSet)

    def test_user_company_detail_route(self):
        url = reverse('user-company-detail', args=[1])
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, UserCompanyAPIViewSet)