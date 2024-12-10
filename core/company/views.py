from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework import status

from company.serializers import (
    CompanySerializer, PositionSerializer, DepartmentSerializer,
    ProjectSerializer, ProjectPostSerializer, DepartmentWithUserInfoSerializer)
from users.serializers import UserEmailSerializer
from company.models import Company, Position, Project, Department
from jwt_registration.models import User
from users.serializers import OnlyUserEmailSerializer
from django.conf import settings
import requests


@extend_schema(
    tags=["Company"],
)
class CompanyAPIViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.prefetch_related('users').all()

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


@extend_schema(
    tags=["Department"]
)
class DepartmentAPIViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.prefetch_related('users').filter(company=self.kwargs['company_pk'])

    def list(self, request, *args, **kwargs):
        departments_response = super().list(request, *args, **kwargs)
        departments_info = departments_response.data

        url = settings.REGISTRATION_SERVICE_URL.format(
            f'profile/api/v1/profile/users-info-by-company/{kwargs["company_pk"]}')
        response = requests.get(url=url)
        if response.status_code != 200:
            return Response({'detail': "company info wasn't get"}, status=response.status_code)
        users_info = response.json()

        for department in departments_info:
            for user in department['users']:
                for user_info in users_info:
                    if user['email'] == user_info['email']:
                        user.update(user_info)
                        break

        departments_info_ser = DepartmentWithUserInfoSerializer(
            departments_info, many=True)

        return Response(departments_info_ser.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        department_response = super().retrieve(request, *args, **kwargs)
        department_info = department_response.data

        url = settings.REGISTRATION_SERVICE_URL.format(
            f'profile/api/v1/profile/users-info-by-company/{kwargs["company_pk"]}')
        response = requests.get(url=url)
        if response.status_code != 200:
            return Response({'detail': "company info wasn't get"}, status=response.status_code)
        users_info = response.json()

        for user in department_info['users']:
            for user_info in users_info:
                if user['email'] == user_info['email']:
                    user.update(user_info)
                    break

        department_info_ser = DepartmentWithUserInfoSerializer(
            department_info)

        return Response(department_info_ser.data, status=status.HTTP_200_OK)


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
