from django.test import TestCase
from django.urls import resolve
from django.urls import reverse
from company.views import CompanyAPIViewSet


class CompanyAPIRouterTestCase(TestCase):

    def test_company_list_route(self):
        url = reverse('company-list')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, CompanyAPIViewSet)

    def test_company_detail_route(self):
        url = reverse('company-detail', args=[1])
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, CompanyAPIViewSet)
