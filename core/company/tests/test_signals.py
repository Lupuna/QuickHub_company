from django.test import TestCase
from jwt_registration.models import User
from company.models import Company, Position
from company.signals import create_company_position


class CreateCompanyPositionTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(email='test_email_1@gmail.com')
        self.user2 = User.objects.create(email='test_email_2@gmail.com')

        self.company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        self.company = Company.objects.create(**self.company_data)

    def test_create_company_position_signal(self):
        self.company.users.add(self.user1, self.user2)
        create_company_position(sender=Company.users.through, instance=self.company, action='post_add')
        position = Position.objects.get(company=self.company)
        self.assertEqual(position.users.count(), 2)
        self.assertTrue(position.users.filter(id=self.user1.id).exists())
        self.assertTrue(position.users.filter(id=self.user2.id).exists())



