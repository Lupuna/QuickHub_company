from django.db.models import Q, Max
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import BasePermission
from company.models import Position
from core.utils import extract_payload
from django.conf import settings


class BaseWeightPermission(BasePermission):
    default_permissions = {
        "view": True, "add": True, "change": True, "delete": True
    }

    priority_permissions = {
        0: {**default_permissions},
        1: {**default_permissions},
        2: {**default_permissions},
        3: {**default_permissions},
        4: {**default_permissions},
        5: {**default_permissions},
    }

    method_to_action = {
        "GET": "view",
        "POST": "add",
        "PUT": "change",
        "PATCH": "change",
        "DELETE": "delete",
    }

    def get_user_email(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise ValidationError({"error": "Authorization header is missing"})
        if not auth_header.startswith(f'{settings.TOKEN_CODE_WORD} '):
            raise ValidationError({"error": f"Invalid token format. Expected {
                                  settings.TOKEN_CODE_WORD} <token>"})

        token = auth_header.split(' ')[1]
        try:
            payload = extract_payload(token)
            return payload.get('email')
        except Exception as e:
            raise ValidationError(
                {"error": f"Failed to extract user ID: {str(e)}"})

    def check_access(self, method, position):
        action = self.method_to_action.get(method)
        if not action:
            raise PermissionDenied(f"Method '{method}' is not supported.")

        permissions = self.priority_permissions.get(position)
        allowed = permissions.get(action)

        if not allowed:
            return False
        return True


class PermissionCompany(BaseWeightPermission):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": False},
        2: {"view": True, "add": True, "change": False, "delete": False},
        3: {"view": True, "add": True, "change": False, "delete": False},
        4: {"view": True, "add": True, "change": False, "delete": False},
        5: {"view": True, "add": True, "change": False, "delete": False},
    }

    def get_position_in_company(self, company_id, user_email):
        position = Position.objects.filter(
            company__id=company_id, users__email=user_email).values('access_weight')
        if position:
            return position[0].get('access_weight')
        raise PermissionDenied('User has no position in provided company')

    def has_permission(self, request, view):
        position = 0

        if self.check_access(request.method, position):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # if request.method == 'GET':
        #     position = 0
        # else:
        position = self.get_position_in_company(
            view.kwargs.get('pk'), self.get_user_email(request))

        if self.check_access(request.method, position):
            return True
        return False


class PermissionProject(PermissionCompany):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": True},
        2: {"view": True, "add": True, "change": True, "delete": False},
        3: {"view": True, "add": False, "change": False, "delete": False},
        4: {"view": True, "add": False, "change": False, "delete": False},
        5: {"view": True, "add": False, "change": False, "delete": False},
    }

    def get_position_in_project(self, company_id, project_id, user_email):
        position = Position.objects.filter(company__id=company_id, users__email=user_email, projects__id=project_id).values(
            project_access_weight=F('project_positions__project_access_weight'))
        if position:
            return position[0].get('project_access_weight')
        raise PermissionDenied('User has no permissons')

    def has_permission(self, request, view):
        position = self.get_position_in_company(
            view.kwargs.get('company_pk'), self.get_user_email(request))

        if self.check_access(request.method, position):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        position = self.get_position_in_project(view.kwargs.get(
            'company_pk'), view.kwargs.get('pk'), self.get_user_email(request))

        if self.check_access(request.method, position):
            return True
        return False


class PermissionDepartment(PermissionCompany):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": True},
        2: {"view": True, "add": False, "change": False, "delete": False},
        3: {"view": True, "add": False, "change": False, "delete": False},
        4: {"view": True, "add": False, "change": False, "delete": False},
        5: {"view": True, "add": False, "change": False, "delete": False},
    }


class PermissionPosition(PermissionCompany):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": True},
        2: {"view": True, "add": False, "change": False, "delete": False},
        3: {"view": True, "add": False, "change": False, "delete": False},
        4: {"view": True, "add": False, "change": False, "delete": False},
        5: {"view": True, "add": False, "change": False, "delete": False},
    }
