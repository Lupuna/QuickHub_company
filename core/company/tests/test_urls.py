from django.test import TestCase
from django.urls import resolve
from django.urls import reverse
from company.views import CompanyAPIViewSet, PositionAPIViewSet, ProjectAPIViewSet, DepartmentAPIViewSet


class CompanyAPIRouterTestCase(TestCase):

    def test_company_list_route(self):
        url = reverse('company-list')
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, CompanyAPIViewSet)

    def test_company_detail_route(self):
        url = reverse('company-detail', args=[1])
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, CompanyAPIViewSet)


class PositionAPIRouterTestCase(TestCase):
    def test_position_list_route(self):
        url = reverse('company-position-list', kwargs={'company_pk': 1})
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, PositionAPIViewSet)

    def test_position_detail_route(self):
        url = reverse('company-position-detail', kwargs={'company_pk': 1, 'pk': 1})
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, PositionAPIViewSet)


class ProjectAPIRouterTestCase(TestCase):
    def test_project_list_route(self):
        url = reverse('company-project-list', kwargs={'company_pk': 1})
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, ProjectAPIViewSet)

    def test_project_detail_route(self):
        url = reverse('company-project-detail', kwargs={'company_pk': 1, 'pk': 1})
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, ProjectAPIViewSet)


class DepartmentAPIRouterTestCase(TestCase):
    def test_department_list_route(self):
        url = reverse('company-department-list', kwargs={'company_pk': 1})
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, DepartmentAPIViewSet)

    def test_department_detail_route(self):
        url = reverse('company-department-detail', kwargs={'company_pk': 1, 'pk': 1})
        resolved_view = resolve(url).func.cls
        self.assertEqual(resolved_view, DepartmentAPIViewSet)
