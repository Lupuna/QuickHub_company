from django.db.models.signals import m2m_changed, post_save
from company.serializers import (
    CompanySerializer, PositionSerializer,
    PositionForProjectSerializer, ProjectSerializer
)
from django.test import TestCase
from jwt_registration.models import User
from company.models import Company, Position, ProjectPosition, Project, Department
from company.signals import create_company_position, create_project_position
from unittest.mock import patch, MagicMock


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
        self.user_data = [{'email': self.user1.email}, {'email': self.user2.email}]
        self.instance = MagicMock()
        self.instance.users = MagicMock()

    def tearDown(self):
        m2m_changed.connect(create_company_position, sender=Company.users.through)

    def test_create_company(self):
        serializer = CompanySerializer(data=self.company_data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()

        self.assertEqual(company.title, self.company_data['title'])
        self.assertEqual(company.description, self.company_data['description'])

    def test_update_company(self):
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

    def test_set_users_create(self):
        CompanySerializer()._set_users(self.instance, self.user_data, created=True)
        self.instance.users.set.assert_called_once()
        called_args = list(self.instance.users.set.call_args[0][0])
        expected_users = [self.user1, self.user2]
        self.assertEqual(called_args, expected_users)

    def test_set_users_update(self):
        CompanySerializer()._set_users(self.instance, self.user_data, created=False)
        self.instance.users.add.assert_called_once()
        self.instance.users.add.assert_called_once()
        called_args = self.instance.users.add.call_args[0][0]
        self.assertEqual(called_args, self.user1)

    def test_set_users_update_remove_users(self):
        CompanySerializer()._set_users(self.instance, self.user_data, created=False, is_remove=True)
        self.instance.users.remove.assert_called_once()
        called_args = list(self.instance.users.remove.call_args[0])
        expected_users = [self.user1, self.user2]
        self.assertEqual(called_args, expected_users)

    @patch('company.serializers.notify_users_created')
    def test_new_users_creation(self, notify_users_created):
        CompanySerializer()._set_users(self.instance, [{'email': 'fake_eamil@gmail.com'}], created=True)
        self.instance.users.set.assert_called_once()
        self.assertTrue(User.objects.filter(email='fake_eamil@gmail.com').exists())


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
        self.department = Department.objects.create(
            title='test_title_department',
            description='test_description',
            company=self.company
        )

        self.instance = MagicMock()
        self.instance.departments = MagicMock()
        self.instance.users = MagicMock()

    def tearDown(self):
        post_save.connect(create_project_position, sender=Project)

    def test_get_positions(self, MockPositionForProjectSerializer):
        mock_positions_data = [
            {'id': self.position1.id, 'title': self.position1.title,
             'access_weight': self.position1.get_access_weight_display()},
            {'id': self.position2.id, 'title': self.position2.title,
             'access_weight': self.position2.get_access_weight_display()},
        ]

        MockPositionForProjectSerializer.return_value.data = mock_positions_data
        serializer = ProjectSerializer(instance=self.project)
        positions_data = serializer.get_positions(self.project)

        self.assertEqual(positions_data, mock_positions_data)

    def test_departments_update(self, MockPositionForProjectSerializer):
        departments_data = {'departments': [{'id': self.department.id, 'title': self.department.title}]}

        serializer = ProjectSerializer(instance=self.project, data=departments_data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        self.assertEqual(list(updated_instance.departments.all()), [self.department])
