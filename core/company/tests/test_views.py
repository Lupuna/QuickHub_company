from django.db.models import Prefetch
from django.urls import reverse
from company.views import PositionAPIViewSet, ProjectAPIViewSet, CompanyAPIViewSet
from company.models import Position, Project
from company.serializers import ProjectPostSerializer, ProjectSerializer
from jwt_registration.models import User
from .test_base import BaseAPITestCase


class CompanyAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.view = CompanyAPIViewSet()

    def test_get_users_for_company(self):
        kwargs = {'pk': self.company.id}
        url = reverse('company-get-users-email-only', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)
        correct_query = User.objects.filter(companies=self.company.id).only('email')
        self.assertQuerySetEqual(self.view.get_users_for_company(), correct_query, ordered=False)

    def test_get_users_email_only(self):
        kwargs = {'pk': self.company.id}
        url = reverse('company-get-users-email-only', kwargs=kwargs)
        response = self.client.get(url)
        self.assertTrue(all(user['email'] for user in response if user in self.company.users.all()))


class PositionAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.view = PositionAPIViewSet()

    def test_get_queryset(self):
        kwargs = {'company_pk': self.company.id}
        url = reverse('company-position-list', kwargs=kwargs)
        request = self.factory.get(url)
        self.view.setup(request, **kwargs)

        correct_query = Position.objects.prefetch_related('users').filter(company=kwargs['company_pk'])
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
