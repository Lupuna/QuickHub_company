from django.db.models import Prefetch
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from company.views import PositionAPIViewSet, ProjectAPIViewSet, UserInCompanyValidateSerializer
from company.models import Company, Position, Project
from company.serializers import ProjectPostSerializer, ProjectSerializer, UserInCompanyValidateSerializer
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


class UserInCompanyValidateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='ali@gmail.com')
        self.company = Company.objects.create(title='ltd')
        self.company.users.add(self.user)
        self.client = self.client_class()

    def test_post(self):
        data1 = {'email': 'ali@gmail.com'}
        data2 = {'email': 'sdff@gmail.com'}
        response1 = self.client.post(
            path=f'http://127.0.0.1:8000/company-service/api/v1/company/{self.company.id}/',
            data=data1,
            format='json'
        )
        response2 = self.client.post(
            f'http://127.0.0.1:8000/company-service/api/v1/company/{self.company.id}/',
            data=data2,
            format='json'
        )

        self.assertEqual(response1.status_code,200)
        self.assertEqual(response1.data['status'],'User in company')
        self.assertEqual(response2.status_code,400)
        self.assertEqual(response2.data['status'],'User is not in company')

