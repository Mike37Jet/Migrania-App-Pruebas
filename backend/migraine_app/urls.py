from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from analiticas.views import AnalisisPatronesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/', include('usuarios.urls')),

    # URLs de otras aplicaciones
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/analiticas/', include('analiticas.urls')),

    # App de evaluación y diagnóstico.
    path('api/', include('evaluacion_diagnostico.urls')),
    
    path('api/', include('tratamiento.urls')),

]