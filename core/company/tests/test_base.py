from rest_framework.test import APITestCase, APIRequestFactory, APIClient

from company.models import Company, Position, Department
from jwt_registration.models import User


class BaseAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(email='test_email_1@gmail.com')
        cls.user2 = User.objects.create(email='test_email_2@gmail.com')
        company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        cls.company = Company.objects.create(**company_data)
        cls.company.users.add(cls.user1, cls.user2)
        cls.factory = APIRequestFactory()
        cls.client = APIClient()

        position_data = {
            'title': 'test_position_title_1',
            'description': 'test_position_description_1',
            'company': cls.company
        }
        cls.position = Position.objects.create(**position_data)

        cls.department = Department.objects.create(
            title='test_dep', company=cls.company)
