from django.db.models import Prefetch
from django.urls import reverse
from company.views import PositionAPIViewSet, ProjectAPIViewSet, CompanyAPIViewSet
from company.models import Company, Position, Project
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
        correct_query = User.objects.filter(companies=self.company.id).only('email').prefetch_related('positions',
                                                                                                      'departments')
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
        correct_query = Project.objects.prefetch_related(prefetch_positions, 'users').filter(
            company=kwargs['company_pk'])
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


class DepartmentAPIViewSetYestCase(BaseAPITestCase):
    def setUp(self):
        self.department.users.add(self.user1)
        self.department.save()
        self.position.users.add(self.user1)
        self.position.save()

    @patch('company.views.requests.get')
    def test_get_users_info_by_dep(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "email": "test_email_1@gmail.com",
                "first_name": "",
                "last_name": "",
                "phone": "",
                "image_identifier": '',
                "date_joined": '',
                "links": [],
                "positions": [
                    {
                        "id": 1,
                        "title": "test_position_title_1",
                        "description": 'test_position_description_1',
                        "access_weight": "Owner",
                        "company": 1,
                        "users": [
                            {
                                "id": 1,
                                "email": "test_email_1@gmail.com"
                            }
                        ]
                    }
                ],
                'departments': [
                    {
                        "id": 2,
                        "title": "test_dep",
                        "description": "",
                        "parent": None,
                        "users": [
                            {
                                "id": 1,
                                "email": "test_email_1@example.com"
                            }
                        ],
                        "color": "rgb(152,219,216)"
                    }
                ]
            },
            {
                "id": 2,
                "email": "test_email_2@gmail.com",
                "first_name": "",
                "last_name": "",
                "phone": "",
                "image_identifier": '',
                "date_joined": '',
                "links": [],
                "positions": [],
                'departments': ['fsf']
            }
        ]
        mock_get.return_value = mock_response

        url = 'http://92.63.67.98:8002' + reverse('company-department-get_users_info_by_dep',
                                                  kwargs={'company_pk': self.company.id, 'dep_pk': self.department.id})
        response = self.client.get(url, HTTP_HOST='92.63.67.98')

        data_expected = [
            {
                "id": 1,
                "email": "test_email_1@gmail.com",
                "first_name": "",
                "last_name": "",
                "phone": "",
                "image_identifier": '',
                "date_joined": '',
                "links": [],
                "positions": [
                    {
                        "id": 1,
                        "title": "test_position_title_1",
                        "description": 'test_position_description_1',
                        "access_weight": "Owner",
                        "company": 1,
                    }
                ]
            }
        ]
        self.assertEqual(response.data, data_expected)
