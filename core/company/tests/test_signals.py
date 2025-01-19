from django.db.models.signals import post_save
from django.test import TestCase
from jwt_registration.models import User
from company.models import Company, Position, Project
from company.signals import create_company_position, create_project_position
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient
from company.tests.test_base import BaseAPITestCase
from django.urls import reverse


class SignalTestCase(BaseAPITestCase):
    def test_create_company_user_not_already_owner(self):
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
        self.assertFalse(Position.objects.filter(
            users__email=self.user3.email))
        response = self.client.post(
            url, data=data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token3}')
        self.assertTrue(Position.objects.filter(
            users__email=self.user3.email))

    def test_create_company_user_already_owner(self):
        url = reverse('company-list')
        data1 = {
            'title': 'hh',
            'users': [
                {
                    "email": self.user3.email
                }
            ],
            'description': 'no',
        }
        response = self.client.post(
            url, data=data1, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token3}')
        data2 = {
            'title': 'hh',
            'users': [
                {
                    "email": self.user3.email
                }
            ],
            'description': 'opa',
        }
        response = self.client.post(
            url, data=data2, format='json', HTTP_AUTHORIZATION=f'Bearer {self.token3}')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'error': 'data_update is required'})


class CreateProjectPositionTestCase(TestCase):

    def setUp(self):
        post_save.disconnect(create_project_position, sender=Project)
        self.company = Company.objects.create(
            title='Test Company',
            description='Test Description'
        )

        self.position1 = Position.objects.create(
            title='Position 1',
            company=self.company
        )
        self.position2 = Position.objects.create(
            title='Position 2',
            company=self.company
        )
        self.project_data = {
            'title': 'test_project_title_1',
            'description': 'test_project_description_1',
            'company': self.company,
        }

    def tearDown(self):
        post_save.connect(create_project_position, sender=Project)

    def test_create_company_position_signal(self):
        project = Project.objects.create(**self.project_data)

        with self.assertNumQueries(2):
            create_project_position(
                sender=Project, instance=project, created=True)

        self.assertEqual(project.positions.count(), 2)
        self.assertTrue(project.positions.filter(
            id=self.position1.id).exists())
        self.assertTrue(project.positions.filter(
            id=self.position2.id).exists())
        self.assertEqual(project.position_projects.count(), 2)
