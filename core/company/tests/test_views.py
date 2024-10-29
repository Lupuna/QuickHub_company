from django.db.models import Prefetch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from company.views import PositionAPIViewSet, ProjectAPIViewSet
from company.models import Company, Position, Project, ProjectPosition
from company.serializers import ProjectPostSerializer, ProjectSerializer
from jwt_registration.models import User


class PositionAPIViewSetTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(email='test_email_1@gmail.com')
        self.user2 = User.objects.create(email='test_email_2@gmail.com')

        company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user1, self.user2)

        self.factory = APIRequestFactory()
        self.view = PositionAPIViewSet()

    def test_get_queryset(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-position-list', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)

        correct_query = Position.objects.prefetch_related('users').filter(company=kwargs['company_pk'])
        self.assertQuerySetEqual(self.view.get_queryset(), correct_query)


class ProjectAPIViewSetTestCase(APITestCase):

    def setUp(self):
        company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        self.company = Company.objects.create(**company_data)
        position_data = {
            'title': 'test_position_title_1',
            'description': 'test_position_description_1',
            'company': self.company
        }
        self.position = Position.objects.create(**position_data)

        self.factory = APIRequestFactory()
        self.view = ProjectAPIViewSet()

    def test_get_queryset(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-project-list', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)

        prefetch_positions = Prefetch(
            'positions',
            queryset=Position.objects.filter(company=kwargs['company_pk']).prefetch_related('project_positions')
            .only('id', 'title', 'access_weight', 'project_positions__project_access_weight')
        )
        correct_query = Project.objects.prefetch_related(prefetch_positions, 'users').filter(company=kwargs['company_pk'])
        self.assertQuerySetEqual(self.view.get_queryset(), correct_query)

    def test_get_serializer(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-project-list', kwargs=kwargs)

        with self.subTest('serializer in post method'):
            request = self.factory.post(url)
            self.view.setup(request, **kwargs)
            self.assertEqual(self.view.get_serializer_class(), ProjectPostSerializer)

        with self.subTest('standard serializer'):
            request = self.factory.get(url)
            self.view.setup(request, **kwargs)
            self.assertEqual(self.view.get_serializer_class(), ProjectSerializer)
