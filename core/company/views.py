from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet
from company.serializers import (
    CompanySerializer, PositionSerializer, DepartmentSerializer,
    ProjectSerializer, ProjectPostSerializer)
from company.models import Company, Position, Project, Department


@extend_schema(
    tags=["Company"]
    )
class CompanyAPIViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.prefetch_related('users').all()


@extend_schema(
    tags=["Position"]
    )
class PositionAPIViewSet(ModelViewSet):
    serializer_class = PositionSerializer

    def get_queryset(self):
        return Position.objects.prefetch_related('users').filter(company=self.kwargs['company_pk'])


@extend_schema(
    tags=["Project"]
    )
class ProjectAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectPostSerializer
        return ProjectSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk')
        prefetch_positions = Prefetch(
            'positions',
            queryset=Position.objects.filter(company=company_id).prefetch_related('project_positions')
            .only('id', 'title', 'access_weight', 'project_positions__project_access_weight')
        )
        return Project.objects.prefetch_related(prefetch_positions, 'users').filter(company=company_id)


@extend_schema(
    tags=["Department"]
    )
class DepartmentAPIViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.prefetch_related('users').filter(company=self.kwargs['company_pk'])
