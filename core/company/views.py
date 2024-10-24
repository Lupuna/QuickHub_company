from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from company.serializers import (
    CompanySerializer, PositionSerializer,
    ProjectSerializer, ProjectPostSerializer)
from company.models import Company, Position, Project


class CompanyAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanySerializer
    queryset = Company.objects.prefetch_related('users').all()


class PositionAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PositionSerializer

    def get_queryset(self):
        return Position.objects.prefetch_related('users').filter(company=self.kwargs['company_pk'])


class ProjectAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectPostSerializer
        return ProjectSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk')
        return Project.objects.prefetch_related('position_projects', 'positions').filter(company=company_id)
