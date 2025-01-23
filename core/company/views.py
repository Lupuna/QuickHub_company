from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework import status
from elasticsearch_dsl import Q

from company.serializers import (
    CompanySerializer, PositionSerializer, DepartmentSerializer,
    ProjectSerializer, ProjectPostSerializer, )
from users.serializers import UserEmailSerializer
from company.models import Company, Position, Project, Department
from jwt_registration.models import User
from users.serializers import OnlyUserEmailSerializer

from company.documents import CompanyDocument, ProjectDocument

from django.db import transaction
from company.utils import *
from company.permissions import PermissionCompany, PermissionProject, PermissionDepartment, PermissionPosition



@extend_schema(
    tags=["Company"],
)
class CompanyAPIViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.prefetch_related('users').all()
    permission_classes = [PermissionCompany, ]

    def list(self, request):
        if request.query_params:
            email = request.query_params["email"]
            query = Q("nested", path="users", query=Q("match", users__email=email))
            result = CompanyDocument.search().filter(query).to_queryset()
            return Response(CompanySerializer(result, many=True).data)
        else:
            return super().list(request)

    def get_users_for_company(self):
        company = self.kwargs['pk']
        return User.objects.filter(companies=company).only('email', ).prefetch_related('positions', 'departments')

    @extend_schema(responses=OnlyUserEmailSerializer, request=OnlyUserEmailSerializer)
    @action(detail=True, methods=['GET'], url_path='users-emails')
    def get_users_email_only(self, request, *args, **kwargs):
        queryset = self.get_users_for_company()
        serializer = OnlyUserEmailSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Position"]
)
class PositionAPIViewSet(ModelViewSet):
    serializer_class = PositionSerializer
    permission_classes = [PermissionPosition, ]

    def get_queryset(self):
        return Position.objects.prefetch_related('users').filter(company=self.kwargs['company_pk'])


@extend_schema(
    tags=["Project"]
)
class ProjectAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [PermissionProject, ]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectPostSerializer
        return ProjectSerializer

    def list(self, request, *args, **kwargs):
        if request.query_params:
            email = request.query_params["email"]
            query = Q("nested", path="users", query=Q("match", users__email=email))
            result = ProjectDocument.search().filter(query).to_queryset()
            return Response(ProjectSerializer(result, many=True).data)
        else:
            return super().list(request)

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk')
        prefetch_positions = Prefetch(
            'positions',
            queryset=Position.objects.filter(
                company=company_id).prefetch_related('project_positions')
            .only('id', 'title', 'access_weight', 'project_positions__project_access_weight')
        )
        prefetch_departments = Prefetch(
            'departments',
            queryset=Department.objects.filter(
                company=company_id).only('id', 'title')
        )
        return Project.objects.prefetch_related(prefetch_positions, prefetch_departments, 'users').filter(company=company_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                project = serializer.save()
                create = CreateTwoCommitsPattern(
                    data={'project': project.id}, service='tasks')
                create.two_commits_operation()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({'error': 'Data is not valid', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Department"]
)
class DepartmentAPIViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [PermissionDepartment, ]

    def get_queryset(self):
        return Department.objects.prefetch_related('users').filter(company=self.kwargs['company_pk'])


@extend_schema(
    tags=['UserInCompanyValidate']
)
class UserInCompanyValidateView(GenericAPIView):
    serializer_class = UserEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserEmailSerializer(data=request.data)
        if serializer.is_valid():
            user_in_company = Company.objects.get(id=self.kwargs['company_pk']).users.filter(
                email=serializer.data.get('email', None)).exists()
            if user_in_company:
                return Response({'status': 'User in company'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'User is not in company'}, status=status.HTTP_400_BAD_REQUEST)
