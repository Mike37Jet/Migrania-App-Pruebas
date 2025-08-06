
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import logging

from usuarios.models import PacienteProfile

logger = logging.getLogger(__name__)

from .models import Tratamiento, Medicamento, Recomendacion, Alerta, Recordatorio
from .serializers import (
    TratamientoCreateSerializer,
    TratamientoSerializer,
    TratamientoResumenSerializer,
    TratamientoCancelarSerializer,
    AlertaSerializer,
    RecordatorioSerializer,
    CambiarEstadoAlertaSerializer,
    NotificacionesPendientesSerializer
)
from .services import TratamientoService
from .repositories import DjangoRepository
from .permissions import (
    EsMedico,
    EsPaciente,
    EsPropietarioDelTratamientoOPersonalMedico,
    PuedeConfirmarToma,
)


class TratamientoViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'], url_path='alertas-sin-confirmar/(?P<paciente_id>[^/.]+)')
    def alertas_sin_confirmar(self, request, paciente_id=None):
        """Obtener todas las alertas en estado SIN_CONFIRMAR de los tratamientos de un paciente"""
        tratamientos = Tratamiento.objects.filter(paciente_id=paciente_id)
        alertas = Alerta.objects.filter(tratamiento__in=tratamientos, estado='sin_confirmar')
        serializer = AlertaSerializer(alertas, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='recordatorios-por-paciente/(?P<paciente_id>[^/.]+)')
    def recordatorios_por_paciente(self, request, paciente_id=None):
        """Obtener todos los recordatorios asociados a los tratamientos de un paciente"""
        tratamientos = Tratamiento.objects.filter(paciente_id=paciente_id)
        recordatorios = Recordatorio.objects.filter(tratamiento__in=tratamientos)
        serializer = RecordatorioSerializer(recordatorios, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='mis-tratamientos')
    def mis_tratamientos(self, request):
        """Devuelve los tratamientos del usuario autenticado (si es paciente)"""
        user = request.user
        if hasattr(user, 'perfil_paciente'):
            tratamientos = Tratamiento.objects.filter(paciente=user.perfil_paciente)
            serializer = self.get_serializer(tratamientos, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'El usuario no es un paciente'}, status=status.HTTP_403_FORBIDDEN)
    @action(detail=True, methods=['post'], url_path='asociar-a-paciente/(?P<paciente_id>\d+)')
    def asociar_a_paciente(self, request, pk=None, paciente_id=None):
        """Asociar un tratamiento existente a un paciente por su id"""
        try:
            try:
                tratamiento = self.get_object()
            except Exception:
                return Response({'success': False, 'error': f'Tratamiento con id {pk} no encontrado o no accesible para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
            try:
                paciente = PacienteProfile.objects.get(id=paciente_id)
            except PacienteProfile.DoesNotExist:
                return Response({'success': False, 'error': f'Paciente con id {paciente_id} no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            tratamiento.paciente = paciente
            tratamiento.save()
            return Response({'success': True, 'mensaje': f'Tratamiento {tratamiento.id} asociado al paciente {paciente_id}'} )
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['get'], url_path='mi-paciente-id')
    def mi_paciente_id(self, request):
        """Devuelve el id del paciente asociado al usuario autenticado"""
        user = request.user
        if hasattr(user, 'perfil_paciente'):
            paciente_id = user.perfil_paciente.id
            return Response({'paciente_id': paciente_id})
        else:
            return Response({'error': 'El usuario no es un paciente'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=False, methods=['get'], url_path='alertas-por-paciente/(?P<paciente_id>[^/.]+)')
    def alertas_por_paciente(self, request, paciente_id=None):
        """Obtener todas las alertas asociadas a los tratamientos de un paciente"""
        tratamientos = Tratamiento.objects.filter(paciente_id=paciente_id)
        alertas = Alerta.objects.filter(tratamiento__in=tratamientos)
        serializer = AlertaSerializer(alertas, many=True)
        return Response(serializer.data)
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = DjangoRepository()
        self.service = TratamientoService(self.repository)

    def get_serializer_class(self):
        if self.action == 'create':
            return TratamientoCreateSerializer
        elif self.action == 'historial':
            return TratamientoResumenSerializer
        elif self.action == 'cancelar':
            return TratamientoCancelarSerializer
        return TratamientoSerializer

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        """
        Filtrar tratamientos según el tipo de usuario:
        - Pacientes: solo ven sus propios tratamientos
        - Médicos: ven todos los tratamientos
        """
        user = self.request.user
        logger.info(f"🔍 get_queryset - Usuario: {user} (ID: {user.id if user else 'None'})")
        
        # Si es un paciente, filtrar por sus propios tratamientos
        if hasattr(user, 'perfil_paciente'):
            paciente_profile = user.perfil_paciente
            queryset = Tratamiento.objects.filter(paciente=paciente_profile)
            logger.info(f"🔍 Usuario es paciente (ID: {paciente_profile.id}), filtrando tratamientos...")
            logger.info(f"🔍 Tratamientos encontrados para paciente: {queryset.count()}")
            return queryset
        
        # Si es médico o personal médico, puede ver todos
        logger.info(f"🔍 Usuario NO es paciente, devolviendo todos los tratamientos")
        all_treatments = Tratamiento.objects.all()
        logger.info(f"🔍 Total de tratamientos en sistema: {all_treatments.count()}")
        return all_treatments

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [EsMedico]
        elif self.action in ['update', 'partial_update', 'destroy', 'modificar', 'cancelar']:
            permission_classes = [EsMedico]
        elif self.action in ['confirmar_toma', 'mis_tratamientos_activos', 'primera_consulta', 
                           'cambiar_estado_alerta', 'mostrar_recordatorio', 'desactivar_recordatorio',
                           'procesar_notificaciones', 'generar_notificaciones']:
            permission_classes = [EsPaciente]
        else:  # list, retrieve, seguimiento, historial, siguiente_alerta, notificaciones_pendientes
            permission_classes = [EsPropietarioDelTratamientoOPersonalMedico]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], url_path='primera-consulta/(?P<paciente_id>[^/.]+)')
    def primera_consulta(self, request, paciente_id=None):
        ultimo_tratamiento = (
            Tratamiento.objects.filter(paciente_id=paciente_id)
            .order_by('-fecha_inicio')
            .first()
        )
        data = {
            'num_episodio': ultimo_tratamiento.id if ultimo_tratamiento else None,
            'tipo_episodio': ultimo_tratamiento.tipo_migraña if ultimo_tratamiento else None,
            'fecha': ultimo_tratamiento.fecha_inicio if ultimo_tratamiento else None
        }
        return Response(data)

    @action(detail=True, methods=['put'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        tratamiento = self.get_object()
        serializer = self.get_serializer(tratamiento, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save(activo=False, fecha_cancelacion=timezone.now())
        self.service.cancelar_notificaciones(tratamiento)

        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='modificar')
    def modificar(self, request, pk=None):
        tratamiento = self.get_object()
        data = request.data

        # Reemplazar medicamentos
        if 'medicamentos' in data:
            tratamiento.medicamentos.clear()
            for med in data['medicamentos']:
                medicamento = Medicamento.objects.get(id=med['id'])
                tratamiento.medicamentos.add(medicamento)

        # Reemplazar recomendaciones
        if 'recomendaciones' in data:
            tratamiento.recomendaciones = [rec['descripcion'] for rec in data['recomendaciones']]
            tratamiento.save()

        self.service.cancelar_notificaciones(tratamiento)
        return Response(self.get_serializer(tratamiento).data)

    @action(detail=False, methods=['get'], url_path='seguimiento/(?P<paciente_id>[^/.]+)')
    def seguimiento(self, request, paciente_id=None):
        tratamiento = (
            Tratamiento.objects.filter(paciente_id=paciente_id, activo=True)
            .order_by('-fecha_inicio')
            .first()
        )
        if not tratamiento:
            return Response({'estado': 'Sin tratamiento'}, status=status.HTTP_200_OK)

        data = {
            'num_episodio': tratamiento.id,
            'tipo_episodio': tratamiento.tipo_migraña,
            'fecha': tratamiento.fecha_inicio,
            'estado': 'Activo',
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='historial/(?P<paciente_id>[^/.]+)')
    def historial(self, request, paciente_id=None):
        tratamientos = (
            Tratamiento.objects.filter(paciente_id=paciente_id)
            .order_by('-fecha_inicio')
        )
        serializer = self.get_serializer(tratamientos, many=True)
        return Response(serializer.data)

    # Nuevos endpoints para notificaciones
    @action(detail=True, methods=['get'], url_path='siguiente-alerta')
    def siguiente_alerta(self, request, pk=None):
        """Obtener la siguiente alerta pendiente de un tratamiento"""
        alerta = self.service.obtener_siguiente_alerta(pk)
        if not alerta:
            return Response(
                {'mensaje': 'No hay alertas pendientes'}, 
                status=status.HTTP_204_NO_CONTENT
            )
        
        serializer = AlertaSerializer(alerta)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='alerta/(?P<alerta_id>\\d+)/estado')
    def cambiar_estado_alerta(self, request, alerta_id=None):
        """Cambiar el estado de una alerta (confirmada/no confirmada)"""
        serializer = CambiarEstadoAlertaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nuevo_estado = serializer.validated_data['nuevo_estado']
        hora_confirmacion = serializer.validated_data.get('hora_confirmacion')
        
        # Mapear los estados del serializer a los del modelo
        estado_mapping = {
            'tomado': 'tomado',
            'no_tomado': 'no_tomado',
            'tomado_tarde': 'tomado_tarde',
            'tomado_muy_tarde': 'tomado_muy_tarde'
        }
        
        estado_modelo = estado_mapping.get(nuevo_estado)
        if not estado_modelo:
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultado = self.service.cambiar_estado_alerta(
            alerta_id, 
            estado_modelo, 
            hora_confirmacion
        )
        
        if not resultado:
            return Response(
                {'error': 'Alerta no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(resultado)

    @action(detail=False, methods=['get'], url_path='recordatorio/(?P<recordatorio_id>\\d+)/mostrar')
    def mostrar_recordatorio(self, request, recordatorio_id=None):
        """Mostrar un recordatorio específico"""
        resultado = self.service.mostrar_recordatorio(recordatorio_id)
        
        if not resultado:
            return Response(
                {'error': 'Recordatorio no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(resultado)

    @action(detail=False, methods=['put'], url_path='recordatorio/(?P<recordatorio_id>\\d+)/desactivar')
    def desactivar_recordatorio(self, request, recordatorio_id=None):
        """Desactivar un recordatorio"""
        try:
            resultado = self.service.desactivar_recordatorio(recordatorio_id)
            
            if not resultado:
                return Response(
                    {'error': 'Recordatorio no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Asegurar que la respuesta sea serializable
            respuesta = {
                'recordatorio_id': resultado['recordatorio_id'],
                'mensaje': resultado['mensaje'],
                'estado_anterior': resultado['estado_anterior'],
                'estado_nuevo': resultado['estado_nuevo'],
                'desactivado': resultado['desactivado']
            }
            
            return Response(respuesta)
            
        except Exception as e:
            # Log del error para debugging
            logger.error(f"Error en desactivar_recordatorio: {str(e)}")
            
            return Response(
                {'error': f'Error interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='notificaciones-pendientes')
    def notificaciones_pendientes(self, request, pk=None):
        """Obtener todas las notificaciones pendientes de un tratamiento"""
        notificaciones = self.service.obtener_notificaciones_pendientes(pk)
        
        # Separar alertas y recordatorios
        alertas = [n for n in notificaciones if isinstance(n, Alerta)]
        recordatorios = [n for n in notificaciones if isinstance(n, Recordatorio)]
        
        data = {
            'alertas': AlertaSerializer(alertas, many=True).data,
            'recordatorios': RecordatorioSerializer(recordatorios, many=True).data,
            'total': len(notificaciones)
        }
        
        serializer = NotificacionesPendientesSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='procesar-notificaciones')
    def procesar_notificaciones(self, request, pk=None):
        """Procesar notificaciones pendientes para reenvío automático"""
        try:
            tratamiento = self.get_object()
            notificaciones_procesadas = tratamiento.procesarNotificacionesPendientes()
            
            # Guardar nuevas alertas creadas
            for notif in notificaciones_procesadas:
                if isinstance(notif, Alerta) and not notif.pk:
                    notif.save()
            
            return Response({
                'procesadas': len(notificaciones_procesadas),
                'mensaje': f'Se procesaron {len(notificaciones_procesadas)} notificaciones'
            })
            
        except Exception as e:
            logger.error(f"Error procesando notificaciones: {str(e)}")
            return Response(
                {'error': f'Error procesando notificaciones: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='generar-notificaciones')
    def generar_notificaciones(self, request, pk=None):
        """Generar notificaciones automáticamente basadas en la frecuencia del tratamiento"""
        try:
            tratamiento = self.get_object()
            
            print(f"🔧 DEBUG: Iniciando generación para tratamiento {tratamiento.id}")
            print(f"🔧 DEBUG: Medicamentos count: {tratamiento.medicamentos.count()}")
            print(f"🔧 DEBUG: Fecha inicio: {tratamiento.fecha_inicio}")
            print(f"🔧 DEBUG: Tratamiento activo: {tratamiento.activo}")
            
            # Generar notificaciones basadas en los medicamentos del tratamiento
            notificaciones_generadas = tratamiento.generarNotificaciones()
            
            print(f"🔧 DEBUG: Notificaciones generadas (total): {len(notificaciones_generadas)}")
            
            # Guardar las notificaciones generadas
            alertas_creadas = 0
            recordatorios_creados = 0
            
            for notificacion in notificaciones_generadas:
                if isinstance(notificacion, Alerta):
                    notificacion.save()
                    alertas_creadas += 1
                elif isinstance(notificacion, Recordatorio):
                    notificacion.save()
                    recordatorios_creados += 1
            
            return Response({
                'generadas': len(notificaciones_generadas),
                'alertas_creadas': alertas_creadas,
                'recordatorios_creados': recordatorios_creados,
                'mensaje': f'Se generaron {len(notificaciones_generadas)} notificaciones ({alertas_creadas} alertas, {recordatorios_creados} recordatorios)'
            })
            
        except Exception as e:
            logger.error(f"Error generando notificaciones: {str(e)}")
            return Response(
                {'error': f'Error generando notificaciones: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
