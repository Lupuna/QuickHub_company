from django.db.models.signals import m2m_changed, post_save
from company.serializers import (
    CompanySerializer, PositionSerializer,
    PositionForProjectSerializer, ProjectSerializer
)
from django.test import TestCase
from jwt_registration.models import User
from company.models import Company, Position, ProjectPosition, Project, Department
from company.signals import create_company_position, create_project_position
from unittest.mock import patch


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

    def test_update_company_with_users(self):
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


class PositionSerializerTestCase(TestCase):

    def setUp(self):
        m2m_changed.disconnect(create_company_position, sender=Company.users.through)
        self.user1 = User.objects.create(email='test_email_1@gmail.com')
        self.user2 = User.objects.create(email='test_email_2@gmail.com')

        company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user1, self.user2)
        self.position_data = {
            'title': 'test_position_title_1',
            'description': 'test_position_description_1',
            'company': self.company.id,
            'users': [
                {'id': self.user1.id, 'email': self.user1.email},
                {'id': self.user2.id, 'email': self.user2.email}
            ],
        }

    def tearDown(self):
        m2m_changed.connect(create_company_position, sender=Company.users.through)

    def test_create_position_with_user(self):
        serializer = PositionSerializer(data=self.position_data)
        serializer.is_valid(raise_exception=True)
        position = serializer.save()

        self.assertEqual(position.title, self.position_data['title'])
        self.assertEqual(position.description, self.position_data['description'])
        self.assertEqual(position.users.count(), 2)
        self.assertIn(self.user1, position.users.all())
        self.assertIn(self.user2, position.users.all())

    def test_update_position_with_user(self):
        position = Position.objects.create(
            title='test_position_title_2',
            description='test_position_description_2',
            company=self.company
        )
        position.users.add(self.user1)
        update_data = {
            'title': 'update_title_company_2',
            'description': 'update_description_company_2',
            'company': self.company.id,
            'users': [{'id': self.user2.id, 'email': self.user2.email}],
        }
        serializer = PositionSerializer(instance=position, data=update_data)
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        self.assertEqual(position.title, update_data['title'])
        self.assertEqual(position.description, update_data['description'])
        self.assertEqual(position.users.count(), 2)
        self.assertIn(self.user1, position.users.all())
        self.assertIn(self.user2, position.users.all())

    def test_get_access_weight_display(self):
        position = Position.objects.create(
            title='test_position_title_2',
            description='test_position_description_2',
            company=self.company
        )
        serializer = PositionSerializer(instance=position)
        access_weight_display = position.get_access_weight_display()
        self.assertEqual(serializer.data['access_weight'], access_weight_display)


class PositionForProjectSerializerTestCase(TestCase):

    def setUp(self):
        self.company = Company.objects.create(title='test_company_title', description='test_company_description')
        self.position = Position.objects.create(
            title='test_position_title',
            description='test_position_description',
            access_weight=Position.WeightChoices.FULL_ACCESS,
            company=self.company
        )

    def test_access_weight_display(self):
        access_weight_display = self.position.get_access_weight_display()
        serializer = PositionForProjectSerializer(instance=self.position)
        self.assertEqual(serializer.data['access_weight'], access_weight_display)

    def test_meta_read_only_fields(self):
        correct_meta_fields = ('id', 'title', 'access_weight')
        self.assertEqual(PositionForProjectSerializer.Meta.read_only_fields, correct_meta_fields)


@patch('company.serializers.PositionForProjectSerializer')
class ProjectSerializerTestCase(TestCase):

    def setUp(self):
        post_save.disconnect(create_project_position, sender=Project)
        self.company = Company.objects.create(
            title='test_company_title',
            description='test_company_description'
        )
        self.position1 = Position.objects.create(
            title='test_position_title_1',
            description='test_position_description_1',
            access_weight=Position.WeightChoices.FULL_ACCESS,
            company=self.company
        )
        self.position2 = Position.objects.create(
            title='test_position_title_2',
            description='test_position_description_2',
            access_weight=Position.WeightChoices.MINIMUM_ACCESS,
            company=self.company
        )
        self.project = Project.objects.create(
            title='test_project_title',
            description='test_project_description',
            company=self.company
        )
        self.project.positions.add(self.position1, self.position2)

        self.project_position = ProjectPosition.objects.create(
            position=self.position1,
            project=self.project,
            project_access_weight=ProjectPosition.WeightChoices.FULL_ACCESS
        )
        self.project.position_projects.add(self.project_position)

    def tearDown(self):
        post_save.connect(create_project_position, sender=Project)

    def test_get_positions(self, MockPositionForProjectSerializer):
        mock_positions_data = [
            {'id': self.position1.id, 'title': self.position1.title, 'access_weight': self.position1.get_access_weight_display()},
            {'id': self.position2.id, 'title': self.position2.title, 'access_weight': self.position2.get_access_weight_display()},
        ]

        MockPositionForProjectSerializer.return_value.data = mock_positions_data
        serializer = ProjectSerializer(instance=self.project)
        positions_data = serializer.get_positions(self.project)

        self.assertEqual(positions_data, mock_positions_data)


class DepartmentSerializerTsetCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(email='test_email_1@gmail.com')
        self.user2 = User.objects.create(email='test_email_2@gmail.com')

        company_data = {
            'title': 'test_company_title_1',
            'description': 'test_company_description_1',
        }
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user1, self.user2)
        self.department_data = {
            'title': 'test_department_title_1',
            'description': 'test_department_description_1',
            'company': self.company.id,
            'users': [
                {'id': self.user1.id, 'email': self.user1.email},
                {'id': self.user2.id, 'email': self.user2.email}
            ],
        }

    def test_create_position_with_user(self):
        serializer = PositionSerializer(data=self.department_data)
        serializer.is_valid(raise_exception=True)
        position = serializer.save()

        self.assertEqual(position.title, self.department_data['title'])
        self.assertEqual(position.description, self.department_data['description'])
        self.assertEqual(position.users.count(), 2)
        self.assertIn(self.user1, position.users.all())
        self.assertIn(self.user2, position.users.all())

    def test_update_position_with_user(self):
        position = Department.objects.create(
            title='test_position_title_2',
            description='test_position_description_2',
            company=self.company
        )
        position.users.add(self.user1)
        update_data = {
            'title': 'update_title_company_2',
            'description': 'update_description_company_2',
            'company': self.company.id,
            'users': [{'id': self.user2.id, 'email': self.user2.email}],
        }
        serializer = PositionSerializer(instance=position, data=update_data)
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        self.assertEqual(position.title, update_data['title'])
        self.assertEqual(position.description, update_data['description'])
        self.assertEqual(position.users.count(), 2)
        self.assertIn(self.user1, position.users.all())
        self.assertIn(self.user2, position.users.all())
