from django.db.models.signals import post_save
from django.test import TestCase
from jwt_registration.models import User
from company.models import Company, Position, Project
from company.signals import create_company_position, create_project_position
from rest_framework.exceptions import ValidationError


class CreateCompanyPositionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='test_email@gmail.com')

        self.company_data1 = {
            'title': 'test_company_title',
            'description': 'test_company_description_1',
        }
        self.company_data2 = {
            'title': 'test_company_title',
            'description': 'test_company_description_2',
        }
        self.kwargs={
            "pk_set": [self.user.id]
        }
        self.company1 = Company.objects.create(**self.company_data1)
        self.company2 = Company.objects.create(**self.company_data2)
        self.id_company2 = self.company2.id


    def test_create_company_position_signal(self):
        self.company1.users.add(self.user)
        create_company_position(sender=Company.users.through, instance=self.company1, action='post_add',**self.kwargs)
        position = Position.objects.get(company=self.company1)
        self.assertEqual(position.users.count(), 1)
        self.assertTrue(position.users.filter(id=self.user.id).exists())
        with self.assertRaises(ValidationError):
            create_company_position(sender=Company.users.through, instance=self.company2, action='pre_add',**self.kwargs)
            self.company2.users.add(self.user)
        self.assertFalse(Company.objects.filter(id=self.id_company2).exists())


class CreateProjectPositionTestCase(TestCase):

    def setUp(self):
        post_save.disconnect(create_project_position, sender=Project)
        self.company = Company.objects.create(
            title='Test Company',
            description='Test Description'
        )

        self.position1 = Position.objects.create(
            title='Position 1',
            company=self.company
        )
        self.position2 = Position.objects.create(
            title='Position 2',
            company=self.company
        )
        self.project_data = {
            'title': 'test_project_title_1',
            'description': 'test_project_description_1',
            'company': self.company,
        }

    def tearDown(self):
        post_save.connect(create_project_position, sender=Project)

    def test_create_company_position_signal(self):
        project = Project.objects.create(**self.project_data)

        with self.assertNumQueries(2):
            create_project_position(sender=Project, instance=project, created=True)

        self.assertEqual(project.positions.count(), 2)
        self.assertTrue(project.positions.filter(id=self.position1.id).exists())
        self.assertTrue(project.positions.filter(id=self.position2.id).exists())
        self.assertEqual(project.position_projects.count(), 2)
