from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from elasticsearch_dsl import Q

from jwt_registration.models import User
from company.models import Company
from users.serializers import UserCompanySerializer
from jwt_registration.documents import UserDocument


@extend_schema(
    tags=["User"]
    )
class UserCompanyAPIViewSet(ReadOnlyModelViewSet):
    serializer_class = UserCompanySerializer

    def list(self, request):
        if request.query_params:
            email = request.query_params["email"]
            query = Q("match", email=email)
            result = UserDocument.search().filter(query).to_queryset()
            return Response(UserCompanySerializer(result, many=True).data)
        else:
            return super().list(request)

    def get_queryset(self):
        company_prefetch = Prefetch(
            'companies',
            queryset=Company.objects.all().only('id', 'title')
        )
        return User.objects.prefetch_related(company_prefetch).all()
