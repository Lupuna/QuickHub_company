from django.urls import path, include
from company.views import CompanyAPIViewSet
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'companies', CompanyAPIViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls))
]