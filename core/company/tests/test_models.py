from django.test import TestCase
from django.contrib.auth import get_user_model
from company.models import Company, Position, Project, ProjectPosition, Department
from django.utils.translation import gettext_lazy as _


class CompanyModelTestCase(TestCase):

    def setUp(self):
        company_data = {
            'title': 'test_company_1',
            'description': 'test_description_1',
        }
        self.user = get_user_model().objects.create_user(email='test_email@gmail.com')
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user)

    def test_str_method(self):
        correct_meaning = self.company.title
        self.assertEqual(correct_meaning, self.company.__str__())

    def test_company_user_relationship(self):
        self.assertIn(self.user, self.company.users.all())

    def test_company_user_removal(self):
        self.company.users.remove(self.user)
        self.assertNotIn(self.user, self.company.users.all())

    def test_meta_verbose_name(self):
        self.assertEqual(Company._meta.verbose_name, _("Company"))

    def test_meta_verbose_name_plural(self):
        self.assertEqual(Company._meta.verbose_name_plural, _("Companies"))

    def test_meta_ordering(self):
        self.assertEqual(Company._meta.ordering, ['title'])


class ProjectModelTestCase(TestCase):

    def setUp(self):
        company_data = {
            'title': 'test_company_1',
            'description': 'test_description_1',
        }
        self.user = get_user_model().objects.create_user(email='test_email@gmail.com')
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user)

        project_data = {
            'title': 'test_project_1',
            'description': 'test_description_1',
            'company': self.company
        }
        self.project = Project.objects.create(**project_data)

    def test_str_method(self):
        correct_meaning = self.project.title
        self.assertEqual(correct_meaning, self.project.__str__())

    def test_meta_verbose_name(self):
        self.assertEqual(Project._meta.verbose_name, _("Project"))

    def test_meta_verbose_name_plural(self):
        self.assertEqual(Project._meta.verbose_name_plural, _("Projects"))

    def test_meta_ordering(self):
        self.assertEqual(Project._meta.ordering, ['title'])


class PositionModelTestCase(TestCase):

    def setUp(self):
        company_data = {
            'title': 'test_company_1',
            'description': 'test_description_1',
        }
        self.user = get_user_model().objects.create_user(email='test_email@gmail.com')
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user)

        project_data = {
            'title': 'test_project_1',
            'description': 'test_description_1',
            'company': self.company
        }
        position_data = {
            'title': 'test_position_title_1',
            'description': 'test_description_1',
            'company': self.company
        }
        self.project = Project.objects.create(**project_data)
        self.position = Position.objects.create(**position_data)
        self.position.projects.add(self.project)
        self.position.users.add(self.user)

    def test_str_method(self):
        correct_meaning = self.position.title
        self.assertEqual(correct_meaning, self.position.__str__())

    def test_meta_verbose_name(self):
        self.assertEqual(Position._meta.verbose_name, _("Position"))

    def test_meta_verbose_name_plural(self):
        self.assertEqual(Position._meta.verbose_name_plural, _("Positions"))

    def test_meta_ordering(self):
        self.assertEqual(Position._meta.ordering, ['access_weight'])

    def test_weight_choices(self):
        correct_choices = [
            (0, _('Owner')),
            (1, _('Setting up project parameters')),
            (2, _('Executing and assigning tasks')),
            (3, _('Executing tasks')),
            (4, _('Observer')),
        ]
        actual_choices = Position.WeightChoices.choices
        self.assertEqual(actual_choices, correct_choices)

    def test_access_weight_choices(self):
        choices = Position._meta.get_field('access_weight').choices
        correct_choices = Position.WeightChoices.choices
        self.assertEqual(choices, correct_choices)

    def test_access_weight_default(self):
        self.assertEqual(self.position.access_weight, Position.WeightChoices.OWNER)


class ProjectPositionTestCase(TestCase):

    def setUp(self):
        company_data = {
            'title': 'test_company_1',
            'description': 'test_description_1',
        }
        self.user = get_user_model().objects.create_user(email='test_email@gmail.com')
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user)

        project_data = {
            'title': 'test_project_1',
            'description': 'test_description_1',
            'company': self.company
        }
        position_data = {
            'title': 'test_position_title_1',
            'description': 'test_description_1',
            'company': self.company
        }
        self.project = Project.objects.create(**project_data)
        self.position = Position.objects.create(**position_data)
        self.position.projects.add(self.project)
        self.position.users.add(self.user)
        self.project_position = ProjectPosition.objects.create(
            position=self.position,
            project=self.project,
            project_access_weight=ProjectPosition.WeightChoices.FULL_ACCESS
        )

    def test_str_method(self):
        expected_str = f"{self.position.title} - {self.project.title}"
        self.assertEqual(str(self.project_position), expected_str)

    def test_weight_choices(self):
        expected_choices = [
            (1, _('Setting up project parameters')),
            (2, _('Executing and assigning tasks')),
            (3, _('Executing tasks')),
            (4, _('Observer')),
            (5, _('Standard')),
        ]
        actual_choices = ProjectPosition.WeightChoices.choices
        self.assertEqual(actual_choices, expected_choices)

    def test_project_access_weight_choices(self):
        field = ProjectPosition._meta.get_field('project_access_weight')
        choices = field.choices
        expected_choices = ProjectPosition.WeightChoices.choices
        self.assertEqual(choices, expected_choices)


class DepartmentTestCase(TestCase):

    def setUp(self):
        company_data = {
            'title': 'test_company_1',
            'description': 'test_description_1',
        }
        self.user = get_user_model().objects.create_user(email='test_email@gmail.com')
        self.company = Company.objects.create(**company_data)
        self.company.users.add(self.user)

        self.department = Department.objects.create(
            title='test_department_1',
            company=self.company
        )
        self.department.users.add(self.user)

    def test_str_method(self):
        correct_meaning = self.department.title
        self.assertEqual(correct_meaning, self.department.__str__())

    def test_company_user_relationship(self):
        self.assertIn(self.user, self.company.users.all())

    def test_company_user_removal(self):
        self.company.users.remove(self.user)
        self.assertNotIn(self.user, self.company.users.all())

    def test_meta_verbose_name(self):
        self.assertEqual(Department._meta.verbose_name, _("Department"))

    def test_meta_verbose_name_plural(self):
        self.assertEqual(Department._meta.verbose_name_plural, _("Departments"))

    def test_color(self):
        self.assertIsNotNone(self.department.color)