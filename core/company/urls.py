from django.urls import path, include
from rest_framework_nested.routers import NestedSimpleRouter

from company.views import CompanyAPIViewSet, PositionAPIViewSet, ProjectAPIViewSet
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'companies', CompanyAPIViewSet, basename='company')

position_router = NestedSimpleRouter(router, r'companies', lookup='company')
position_router.register(r'positions', PositionAPIViewSet, basename='company-position')

project_router = NestedSimpleRouter(router, r'companies', lookup='company')
project_router.register(r'projects', ProjectAPIViewSet, basename='company-project')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(position_router.urls)),
    path('api/v1/', include(project_router.urls)),
]