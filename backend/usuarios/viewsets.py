# usuarios/viewsets.py 
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import MedicoProfile, PacienteProfile, EnfermeraProfile
from .serializers import (
    UsuarioCompletoSerializer, 
    RegistroMedicoSerializer, 
    RegistroPacienteSerializer, 
    RegistroEnfermeraSerializer
)
from .permissions import EsMedicoOEnfermera
from .services import usuario_service

Usuario = get_user_model()


#  VIEWSET PROTEGIDO - Solo para usuarios autenticados
@extend_schema_view(tags=["Usuarios"])
class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """Gestión de usuarios - Solo lectura y acciones específicas"""
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Usuarios ven solo su info, personal médico ve todo"""
        user = self.request.user
        if user.es_medico or user.es_enfermera:
            return usuario_service.obtener_todos_usuarios()
        else:
            return [usuario_service.obtener_usuario_por_id(user.id)]
    
    @action(detail=False, methods=['get'])
    def mi_perfil(self, request):
        """ GET /api/usuarios/mi-perfil/ - Perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """ GET /api/usuarios/dashboard/ - Dashboard según rol"""
        user = request.user
        dashboard_data = usuario_service.generar_dashboard_datos(user)
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'], permission_classes=[EsMedicoOEnfermera])
    def medicos(self, request):
        """ GET /api/usuarios/medicos/ - Lista médicos (solo personal médico)"""
        data = usuario_service.obtener_lista_medicos_resumida()
        return Response(data)
    
    @action(detail=False, methods=['get'], permission_classes=[EsMedicoOEnfermera])
    def pacientes(self, request):
        """ GET /api/usuarios/pacientes/ - Lista pacientes (solo personal médico)"""
        data = usuario_service.obtener_lista_pacientes_resumida()
        return Response(data)
    
    @action(detail=False, methods=['get'], permission_classes=[EsMedicoOEnfermera])
    def enfermeras(self, request):
        """ GET /api/usuarios/enfermeras/ - Lista enfermeras (solo personal médico)"""
        data = usuario_service.obtener_lista_enfermeras_resumida()
        return Response(data)

# VIEWSETS PÚBLICOS DE REGISTRO (sin autenticación)

@extend_schema_view(tags=["Registro"])
class RegistroMedicoViewSet(viewsets.GenericViewSet):
    """ Registro de médicos - Público con formulario DRF"""
    serializer_class = RegistroMedicoSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Usuario.objects.none()
    
    def list(self, request):
        """GET /api/registro-medico/ - Muestra formulario de registro"""
        return Response({
            'message': 'Registro de médicos',
            'instruction': 'Complete el formulario para registrar un nuevo médico',
            'endpoint_info': {
                'method': 'POST',
                'url': '/api/registro-medico/',
                'content_type': 'application/json'
            }
        })
    
    def create(self, request):
        """POST /api/registro-medico/ - Crear médico"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Médico registrado exitosamente',
                'usuario': {
                    'id': user.id,
                    'email': user.email,
                    'nombre_completo': user.get_full_name(),
                    'tipo_usuario': user.tipo_usuario
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Error en el registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(tags=["Registro"])
class RegistroPacienteViewSet(viewsets.GenericViewSet):
    """ Registro de pacientes - Público con formulario DRF"""
    serializer_class = RegistroPacienteSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Usuario.objects.none()
    
    def list(self, request):
        """GET /api/registro-paciente/ - Muestra formulario de registro"""
        return Response({
            'message': 'Registro de pacientes',
            'instruction': 'Complete el formulario para registrar un nuevo paciente',
            'endpoint_info': {
                'method': 'POST',
                'url': '/api/registro-paciente/',
                'content_type': 'application/json'
            }
        })
    
    def create(self, request):
        """POST /api/registro-paciente/ - Crear paciente"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Paciente registrado exitosamente',
                'usuario': {
                    'id': user.id,
                    'email': user.email,
                    'nombre_completo': user.get_full_name(),
                    'tipo_usuario': user.tipo_usuario
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Error en el registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(tags=["📝 Registro"])
class RegistroEnfermeraViewSet(viewsets.GenericViewSet):
    """ Registro de enfermeras - Público con formulario DRF"""
    serializer_class = RegistroEnfermeraSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Usuario.objects.none()
    
    def list(self, request):
        """GET /api/registro-enfermera/ - Muestra formulario de registro"""
        return Response({
            'message': 'Registro de enfermeras',
            'instruction': 'Complete el formulario para registrar una nueva enfermera',
            'endpoint_info': {
                'method': 'POST',
                'url': '/api/registro-enfermera/',
                'content_type': 'application/json'
            }
        })
    
    def create(self, request):
        """POST /api/registro-enfermera/ - Crear enfermera"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Enfermera registrada exitosamente',
                'usuario': {
                    'id': user.id,
                    'email': user.email,
                    'nombre_completo': user.get_full_name(),
                    'tipo_usuario': user.tipo_usuario
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Error en el registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)