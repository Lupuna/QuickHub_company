from company.models import *
from company.permissions import *
from company.tests.test_base import BaseAPITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from company.serializers import CompanySerializer
from unittest.mock import patch, MagicMock


class PermissionCompanyTestCase(BaseAPITestCase):
    def test_view_allowed(self):
        url = reverse('company-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_allowed(self):
        url = reverse('company-list')
        data = {
            'title': 'hh',
            'users': [
                {
                    "email": self.user3.email
                }
            ],
            'description': 'no',
        }
        response = self.client.post(
            url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token3}', format='json')
        self.assertEqual(response.status_code, 201)

    def test_change_ok(self):
        url = reverse('company-detail', kwargs={'pk': self.company.id})
        new_data = {
            'title': 'new title'
        }
        response = self.client.patch(
            url, data=new_data, HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Company.objects.get(
            id=self.company.id).title, 'new title')

    def test_change_forbidden(self):
        url = reverse('company-detail', kwargs={'pk': self.company.id})
        new_data = {
            'title': 'new title'
        }
        response = self.client.patch(
            url, data=new_data, HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Company.objects.get(
            id=self.company.id).title, self.company.title)

    def test_del_allowed(self):
        url = reverse('company-detail', kwargs={'pk': self.company.id})
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f'Bearer {self.token1}')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            len(Company.objects.all()), 1
        )

    def test_del_forbidden(self):
        url = reverse('company-detail', kwargs={'pk': self.company.id})
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f'Bearer {self.token2}')

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Company.objects.all())


class PermissionProjectTestCase(BaseAPITestCase):
    def setUp(self):
        self.project = self.project1
        pos_us_1 = ProjectPosition.objects.filter(
            position=self.position)[0]
        pos_us_1.project_access_weight = 1
        pos_us_1.save()

    def test_view_allowed(self):
        url = reverse('company-project-list',
                      kwargs={'company_pk': self.company.id})
        response = self.client.get(
            url, HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        self.assertEqual(response.status_code, 200)

    @patch('company.utils.TwoCommitsPattern.two_commits_operation')
    def test_add_allowed(self, mock_two_commits):
        mock_two_commits.return_value = {'task': 200}
        url = reverse('company-project-list',
                      kwargs={'company_pk': self.company.id})
        data = {
            "company": self.company.id,
            "title": "proj",
            "users": [
                {
                    "email": self.user1.email
                }
            ],
        }
        response = self.client.post(
            url, data=data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(title='proj'))

    def test_add_forbidden(self):
        url = reverse('company-project-list',
                      kwargs={'company_pk': self.company.id})
        data = {
            "company": self.company.id,
            "title": "proj",
            "users": [
                {
                    "email": self.user2.email
                }
            ],
        }

        response = self.client.post(
            url, data=data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        self.assertEqual(response.status_code, 403)

    def test_change_allowed(self):
        url = reverse('company-project-detail',
                      kwargs={'company_pk': self.company.id, 'pk': self.project.id})
        data = {
            'title': 'new title'
        }
        response = self.client.patch(
            url, data=data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Project.objects.filter(title='new title'))
        self.assertFalse(Project.objects.filter(title='test proj'))

    def test_change_forbidden(self):
        url = reverse('company-project-detail',
                      kwargs={'company_pk': self.company.id, 'pk': self.project.id})
        data = {
            'title': 'new title'
        }
        response = self.client.patch(
            url, data=data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.filter(title='new title'))

    def test_delete_allowed(self):
        url = reverse('company-project-detail',
                      kwargs={'company_pk': self.company.id, 'pk': self.project.id})
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f'Bearer {self.token1}')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Project.objects.filter(title='test proj'))

    def delete_forbidden(self):
        url = reverse('company-project-detail',
                      kwargs={'company_pk': self.company.id, 'pk': self.project.id})
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f'Bearer {self.token2}')

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(title='test proj'))
