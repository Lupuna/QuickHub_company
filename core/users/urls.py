from django.urls import path, include
from rest_framework.routers import SimpleRouter
from users.views import UserCompanyAPIViewSet


company_user_router = SimpleRouter()
company_user_router.register(r'companies', UserCompanyAPIViewSet, basename='user-company')

urlpatterns = [
    path('', include(company_user_router.urls))
]