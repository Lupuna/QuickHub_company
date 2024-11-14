from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('company-service/admin/', admin.site.urls),
    path('company-service/api/v1/company/users/', include('users.urls')),
    path('company-service/api/v1/company/registration/', include('jwt_registration.urls')),
    path('company-service/api/v1/company/', include('company.urls')),
    path('company-service/schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('company-service/docs/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls")), ]
