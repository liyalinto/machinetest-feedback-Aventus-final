# feedback_project/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Feedback Management API",
        default_version='v1',
        description="API documentation for the Employee Feedback Management System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def home(request):
    return JsonResponse({
        "message": "Welcome to the Feedback Management API",
        "swagger_ui": "/swagger/",
        "redoc_ui": "/redoc/",
        "endpoints": [
            "/api/auth/register/",
            "/api/auth/login/",
            "/api/questions/",
            "/api/feedback/submit/",
            "/api/feedback/my/",
            "/api/feedback/admin/"
        ]
    })

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/', include('feedback.urls')),

    # Swagger UI and JSON
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]