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

    def has_permission(self, request, view):
        position = self.get_position_weight(request.kwargs.get('company_pk'), self.get_user_email(request))

        if self.check_access(request.method, position):
            return True
        else: return False

    def get_user_email(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise ValidationError({"error": "Authorization header is missing"})
        if not auth_header.startswith(f'{settings.TOKEN_CODE_WORD} '):
            raise ValidationError({"error": f"Invalid token format. Expected '{settings.TOKEN_CODE_WORD} <token>'"})

        token = auth_header.split(' ')[1]
        try:
            payload = extract_payload(token)
            return payload.get('email')
        except Exception as e:
            raise ValidationError({"error": f"Failed to extract user ID: {str(e)}"})

    def get_position_weight(self, company, user_id):
        position_with_max_weight = Position.objects.filter(
            Q(company=company) & Q(users__email=user_id)
        ).annotate(max_weight=Max('priority')).order_by('-max_priority').first()

        if not position_with_max_weight:
            raise PermissionDenied("No position found or insufficient permissions.")
        return position_with_max_weight

    def check_access(self, method, position):
        action = self.method_to_action.get(method)
        if not action:
            raise PermissionDenied(f"Method '{method}' is not supported.")

        permissions = self.priority_permissions.get(position.priority, {})
        if not permissions.get(action, False):
            raise PermissionDenied(
                f"Action '{action}' is not allowed for priority {position.priority}."
            )
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

    def has_permission(self, request, view):
        position = self.get_position_weight(request.kwargs.get('pk'), self.get_user_email(request))

        if self.check_access(request.method, position):
            return True
        else: return False


class PermissionProject(BaseWeightPermission):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": True},
        2: {"view": True, "add": True, "change": True, "delete": False},
        3: {"view": True, "add": False, "change": False, "delete": False},
        4: {"view": True, "add": False, "change": False, "delete": False},
        5: {"view": True, "add": False, "change": False, "delete": False},
    }


class PermissionDepartment(BaseWeightPermission):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": True},
        2: {"view": True, "add": False, "change": False, "delete": False},
        3: {"view": True, "add": False, "change": False, "delete": False},
        4: {"view": True, "add": False, "change": False, "delete": False},
        5: {"view": True, "add": False, "change": False, "delete": False},
    }


class PermissionPosition(BaseWeightPermission):
    priority_permissions = {
        0: {"view": True, "add": True, "change": True, "delete": True},
        1: {"view": True, "add": True, "change": True, "delete": True},
        2: {"view": True, "add": False, "change": False, "delete": False},
        3: {"view": True, "add": False, "change": False, "delete": False},
        4: {"view": True, "add": False, "change": False, "delete": False},
        5: {"view": True, "add": False, "change": False, "delete": False},
    }
