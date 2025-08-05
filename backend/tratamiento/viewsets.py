from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

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

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [EsMedico]
        elif self.action in ['update', 'partial_update', 'destroy', 'modificar', 'cancelar']:
            permission_classes = [EsMedico]
        elif self.action in ['confirmar_toma', 'mis_tratamientos_activos', 'primera_consulta', 
                           'cambiar_estado_alerta', 'mostrar_recordatorio', 'desactivar_recordatorio']:
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
        TratamientoService.cancelar_notificaciones(tratamiento)

        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='modificar')
    def modificar(self, request, pk=None):
        tratamiento = self.get_object()
        data = request.data

        # Actualizar campos principales
        tratamiento.frecuencia = data.get('frecuencia', tratamiento.frecuencia)
        tratamiento.duracion_dias = data.get('duracion_dias', tratamiento.duracion_dias)
        tratamiento.hora_de_inicio = data.get('hora_de_inicio', tratamiento.hora_de_inicio)
        tratamiento.save()

        # Reemplazar medicamentos
        if 'medicamentos' in data:
            tratamiento.medicamentos.clear()
            for med in data['medicamentos']:
                medicamento = Medicamento.objects.get(id=med['id'])
                tratamiento.medicamentos.add(medicamento)

        # Reemplazar recomendaciones
        if 'recomendaciones' in data:
            tratamiento.recomendaciones.clear()
            for rec in data['recomendaciones']:
                Recomendacion.objects.create(tratamiento=tratamiento, descripcion=rec['descripcion'])

        TratamientoService.cancelar_notificaciones(tratamiento)
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
        resultado = self.service.desactivar_recordatorio(recordatorio_id)
        
        if not resultado:
            return Response(
                {'error': 'Recordatorio no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(resultado)

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
