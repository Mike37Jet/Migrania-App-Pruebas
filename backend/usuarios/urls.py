# usuarios/urls.py 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    UsuarioViewSet,
    RegistroMedicoViewSet, 
    RegistroPacienteViewSet, 
    RegistroEnfermeraViewSet
)
from .views import (
    opciones_formulario,
    validar_cedula,
    validar_email
)

router = DefaultRouter()

# ENDPOINTS PROTEGIDOS (requieren autenticación)
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

# ENDPOINTS PÚBLICOS DE REGISTRO (formularios DRF + API)
router.register(r'registro-medico', RegistroMedicoViewSet, basename='registro-medico')
router.register(r'registro-paciente', RegistroPacienteViewSet, basename='registro-paciente')  
router.register(r'registro-enfermera', RegistroEnfermeraViewSet, basename='registro-enfermera')

urlpatterns = [
    # Router principal
    path('', include(router.urls)),

    # UTILIDADES PÚBLICAS
    path('opciones-formulario/', opciones_formulario, name='opciones-formulario'),
    path('validar-cedula/', validar_cedula, name='validar-cedula'),
    path('validar-email/', validar_email, name='validar-email'),
]