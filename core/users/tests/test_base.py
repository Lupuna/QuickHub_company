from rest_framework.test import APITestCase
from jwt_registration.models import User
from company.models import Company


class BaseAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.valid_data_1 = {
            'email': 'test1@example.com',
        }

        cls.valid_data_2 = {
            'email': 'test2@example.com',
        }

        cls.valid_data_3 = {
            'email': 'new_email@example.com',
        }

        cls.user_1 = User.objects.create_user(**cls.valid_data_1)
        cls.user_2 = User.objects.create_user(**cls.valid_data_2)
        cls.user_3 = User.objects.create_user(**cls.valid_data_3)
        cls.company = Company.objects.create(
            title='test-company_title',
            description='test_company_description',
        )
        cls.company.users.set((cls.user_1, cls.user_2, cls.user_3))
