from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/company/users/', include('users.urls')),
    path('api/v1/company/registration/', include('jwt_registration.urls')),
    path('api/v1/company/', include('company.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls")), ]
