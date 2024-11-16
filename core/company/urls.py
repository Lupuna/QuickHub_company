from django.urls import path, include
from rest_framework_nested.routers import NestedSimpleRouter

from company.views import CompanyAPIViewSet, PositionAPIViewSet, ProjectAPIViewSet, DepartmentAPIViewSet, UserInCompanyValidateView
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'companies', CompanyAPIViewSet, basename='company')

position_router = NestedSimpleRouter(router, r'companies', lookup='company')
position_router.register(r'positions', PositionAPIViewSet, basename='company-position')

project_router = NestedSimpleRouter(router, r'companies', lookup='company')
project_router.register(r'projects', ProjectAPIViewSet, basename='company-project')

department_router = NestedSimpleRouter(router, r'companies', lookup='company')
department_router.register(r'departments', DepartmentAPIViewSet, basename='company-department')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(position_router.urls)),
    path('', include(project_router.urls)),
    path('', include(department_router.urls)),
    path('<int:company_pk>/',UserInCompanyValidateView.as_view()),
]