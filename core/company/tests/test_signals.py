from django.db.models.signals import post_save
from django.test import TestCase
from jwt_registration.models import User
from company.models import Company, Position, Project
from company.signals import create_company_position, create_project_position


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
