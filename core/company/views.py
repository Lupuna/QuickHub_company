from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from company.serializers import CompanySerializer
from company.models import Company


class CompanyAPIViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.select_related('projects').prefetch_related('users').all()


