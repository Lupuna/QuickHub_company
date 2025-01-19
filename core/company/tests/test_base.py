from rest_framework.test import APITestCase, APIRequestFactory, APIClient

from company.models import Company, Position, Department, Project, ProjectPosition
from jwt_registration.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class BaseAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(email='test_email_1@gmail.com')
        cls.user2 = User.objects.create(email='test_email_2@gmail.com')
        cls.user3 = User.objects.create(email='test_email_3@gmail.com')

        token1 = RefreshToken.for_user(cls.user1)
        token1.payload.update({'email': cls.user1.email})
        cls.token1 = str(token1)

        token2 = RefreshToken.for_user(cls.user2)
        token2.payload.update({'email': cls.user2.email})
        cls.token2 = str(token2)

        token3 = RefreshToken.for_user(cls.user3)
        token3.payload.update({'email': cls.user3.email})
        cls.token3 = str(token3)

        company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        cls.company = Company.objects.create(**company_data)
        cls.company.users.add(cls.user1)
        cls.company.users.add(cls.user2)
        cls.factory = APIRequestFactory()
        cls.client = APIClient()

        position_data_for_user_2 = {
            'title': 'test_position_title_1',
            'description': 'test_position_description_1',
            'company': cls.company,
            'access_weight': 5
        }
        cls.position = Position.objects.create(**position_data_for_user_2)
        cls.position.users.add(cls.user2)

        cls.department = Department.objects.create(
            title='test_dep', company=cls.company)
