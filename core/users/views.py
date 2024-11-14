from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ReadOnlyModelViewSet
from jwt_registration.models import User
from company.models import Company
from users.serializers import UserCompanySerializer


@extend_schema(
    tags=["User"]
    )
class UserCompanyAPIViewSet(ReadOnlyModelViewSet):
    serializer_class = UserCompanySerializer

    def get_queryset(self):
        company_prefetch = Prefetch(
            'companies',
            queryset=Company.objects.all().only('id', 'title')
        )
        return User.objects.prefetch_related(company_prefetch).all()
