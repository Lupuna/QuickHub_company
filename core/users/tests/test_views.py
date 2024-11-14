from django.db.models import Prefetch
from django.urls import reverse

from company.models import Company
from jwt_registration.models import User
from users.views import UserCompanyAPIViewSet
from .test_base import BaseAPITestCase
from rest_framework.test import APIRequestFactory


class UserCompanyAPIViewSetTestCase(BaseAPITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = reverse('user-list')
        self.view = UserCompanyAPIViewSet()

    def test_get_queryset(self):
        request = self.factory.get(self.url)
        self.view.setup(request)

        company_prefetch = Prefetch(
            'companies',
            queryset=Company.objects.all().only('id', 'title')
        )
        correct_query = User.objects.prefetch_related(company_prefetch).all()
        self.assertQuerySetEqual(self.view.get_queryset(), correct_query, ordered=False)