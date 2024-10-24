from django.test import TestCase
from jwt_registration.models import User
from django.core import mail


class TestUserModelTestCase(TestCase):

    def setUp(self):
        self.data = {
            'email': 'test_email@gmail.com',
        }
        self.mail_data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'from_email': 'admin@example.com'
        }
        self.user = User.objects.create(**self.data)

    def test_user_creation(self):
        self.assertEqual(self.user.email, self.data['email'])
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_str_method(self):
        correct_meaning = self.user.email
        self.assertEqual(str(self.user), correct_meaning)

    def test_email_user(self):
        self.user.email_user(**self.mail_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.mail_data['subject'])
        self.assertEqual(mail.outbox[0].body, self.mail_data['message'])
        self.assertEqual(mail.outbox[0].from_email, self.mail_data['from_email'])
        self.assertEqual(mail.outbox[0].to, [self.user.email])
