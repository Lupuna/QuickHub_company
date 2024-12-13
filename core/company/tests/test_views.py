from django.db.models import Prefetch
from django.urls import reverse
from company.views import PositionAPIViewSet, ProjectAPIViewSet, CompanyAPIViewSet
from company.models import Company, Position, Project, Department
from company.serializers import ProjectPostSerializer, ProjectSerializer
from jwt_registration.models import User
from .test_base import BaseAPITestCase
from unittest.mock import patch, MagicMock


class CompanyAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.view = CompanyAPIViewSet()

    def test_get_users_for_company(self):
        kwargs = {'pk': self.company.id}
        url = reverse('company-get-users-email-only', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)
        correct_query = User.objects.filter(companies=self.company.id).only(
            'email').prefetch_related('positions', 'departments')
        self.assertQuerySetEqual(
            self.view.get_users_for_company(), correct_query, ordered=False)

    def test_get_users_email_only(self):
        kwargs = {'pk': self.company.id}
        url = reverse('company-get-users-email-only', kwargs=kwargs)
        response = self.client.get(url)
        self.assertTrue(
            all(user['email'] for user in response if user in self.company.users.all()))


class PositionAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.view = PositionAPIViewSet()

    def test_get_queryset(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-position-list', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)

        correct_query = Position.objects.prefetch_related(
            'users').filter(company=kwargs['company_pk'])
        self.assertQuerySetEqual(self.view.get_queryset(), correct_query)


class ProjectAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.view = ProjectAPIViewSet()

    def test_get_queryset(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-project-list', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)

        prefetch_positions = Prefetch(
            'positions',
            queryset=Position.objects.filter(
                company=kwargs['company_pk']).prefetch_related('project_positions')
            .only('id', 'title', 'access_weight', 'project_positions__project_access_weight')
        )
        prefetch_departments = Prefetch(
            'departments',
            queryset=Department.objects.filter(
                company=kwargs['company_pk']).only('id', 'title')
        )
        correct_query = Project.objects.prefetch_related(
            prefetch_positions,
            prefetch_departments,
            'users'
        ).filter(company=kwargs['company_pk'])
        self.assertQuerySetEqual(self.view.get_queryset(), correct_query)

    def test_get_serializer(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-project-list', kwargs=kwargs)

        with self.subTest('serializer in post method'):
            request = self.factory.post(url)
            self.view.setup(request, **kwargs)
            self.assertEqual(self.view.get_serializer_class(),
                             ProjectPostSerializer)

        with self.subTest('standard serializer'):
            request = self.factory.get(url)
            self.view.setup(request, **kwargs)
            self.assertEqual(self.view.get_serializer_class(),
                             ProjectSerializer)


class UserInCompanyValidateTest(BaseAPITestCase):
    def setUp(self):
        self.user = User.objects.create(email='ali@gmail.com')
        self.company = Company.objects.create(title='ltd')
        self.company.users.add(self.user)
        self.client = self.client_class()

    def test_post(self):
        data1 = {'email': 'ali@gmail.com'}
        data2 = {'email': 'sdff@gmail.com'}
        response1 = self.client.post(
            path=reverse('user-in-company', kwargs={'company_pk': self.company.id}),
            data=data1,
            format='json'
        )
        response2 = self.client.post(
            path=reverse('user-in-company', kwargs={'company_pk': self.company.id}),
            data=data2,
            format='json'
        )

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['status'], 'User in company')
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data['status'], 'User is not in company')
