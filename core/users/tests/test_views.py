from django.db.models import Prefetch
from django.urls import reverse

from company.models import Company
from jwt_registration.models import User
from users.views import UserCompanyAPIViewSet
from .test_base import BaseAPITestCase
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.request import Request


class UserCompanyAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = reverse('user-list')
        self.view = UserCompanyAPIViewSet()
        self.client = APIClient()

    def test_get_queryset(self):
        request = self.factory.get(self.url)
        self.view.setup(request)

        company_prefetch = Prefetch(
            'companies',
            queryset=Company.objects.all().only('id', 'title')
        )
        correct_query = User.objects.prefetch_related(company_prefetch).all()
        self.assertQuerySetEqual(self.view.get_queryset(), correct_query, ordered=False)

    def test_with_query_params(self):
        url = reverse('user-company-list')
        response = self.client.get(url, {"email": self.user_1.email})
        self.assertEqual(
            len(response.data), 1
        )
        self.assertEqual(
            self.user_1.email, response.data[0]["email"]
        )

    def test_without_query_params(self):
        url = reverse('user-company-list')
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), 3
        )