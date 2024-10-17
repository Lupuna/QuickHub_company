from django.db.models.signals import m2m_changed
from company.serializers import CompanySerializer
from django.test import TestCase
from jwt_registration.models import User
from company.models import Company
from company.signals import create_company_position


class CompanySerializerTest(TestCase):

    def setUp(self):
        m2m_changed.disconnect(create_company_position, sender=Company.users.through)
        self.user1 = User.objects.create(email='test_email_1@gmail.com')
        self.user2 = User.objects.create(email='test_email_2@gmail.com')

        self.company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
            'users': [
                {'id': self.user1.id, 'email': self.user1.email},
                {'id': self.user2.id, 'email': self.user2.email}
            ],
        }

    def tearDown(self):
        m2m_changed.connect(create_company_position, sender=Company.users.through)

    def test_create_company_with_users(self):
        serializer = CompanySerializer(data=self.company_data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()

        self.assertEqual(company.title, self.company_data['title'])
        self.assertEqual(company.description, self.company_data['description'])
        self.assertEqual(company.users.count(), 2)
        self.assertIn(self.user1, company.users.all())
        self.assertIn(self.user2, company.users.all())

    def test_update_company_users(self):
        company = Company.objects.create(title='test_company_title_2', description='test_company_description_2')
        company.users.add(self.user1)
        update_data = {
            'title': 'update_title_company_2',
            'description': 'update_description_company_2',
            'users': [{'id': self.user2.id, 'email': self.user2.email}],
        }

        serializer = CompanySerializer(instance=company, data=update_data)
        serializer.is_valid(raise_exception=True)
        updated_company = serializer.save()

        self.assertEqual(updated_company.title, update_data['title'])
        self.assertEqual(updated_company.description, update_data['description'])
        self.assertEqual(updated_company.users.count(), 2)
        self.assertIn(self.user2, updated_company.users.all())
        self.assertIn(self.user1, updated_company.users.all())