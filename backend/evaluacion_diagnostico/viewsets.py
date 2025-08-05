from rest_framework import viewsets, mixins, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Pregunta, Respuesta, AutoevaluacionMidas
from .permissions import EsPaciente, EsPropietarioDeLaAutoevaluacionOPersonalMedico
from .autoevaluacion_midas_service import autoevaluacion_midas_service
from .episodio_cefalea_service import episodio_cefalea_service
from .models import EpisodioCefalea
from .permissions import EsPropietarioDelEpisodioOPersonalMedico
from .serializers import CrearEpisodioCefaleaSerializer, EpisodioCefaleaSerializer

from .serializers import (
    PreguntaSerializer,
    CrearAutoevaluacionSerializer, AutoevaluacionMidasSerializer,
    CrearRespuestaSerializer, RespuestaSerializer,
)


class PreguntaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet para manejar las preguntas de la autoevaluación MIDAS.
    Permite listar y ver los detalles de las preguntas.
    """
    queryset = Pregunta.objects.all().order_by('orden_pregunta')
    serializer_class = PreguntaSerializer
    permission_classes = [permissions.IsAuthenticated]


class AutoevaluacionMidasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las autoevaluaciones MIDAS.
    Permite crear, listar y ver autoevaluaciones.
    """
    queryset = AutoevaluacionMidas.objects.select_related("paciente").all()
    permission_classes = [permissions.IsAuthenticated, EsPropietarioDeLaAutoevaluacionOPersonalMedico]

    def get_serializer_class(self):
        """
        Devuelve el serializer adecuado según la acción.
        """
        if self.action == 'create':
            return CrearAutoevaluacionSerializer
        return AutoevaluacionMidasSerializer

    def get_queryset(self):
        user = self.request.user
        if user.es_medico or user.es_enfermera:
            return self.queryset
        return self.queryset.filter(paciente=user)

    def perform_create(self, serializer):
        """
        Guarda la autoevaluación MIDAS creada por el paciente.
        """
        paciente = self.request.user
        ultima = AutoevaluacionMidas.objects.filter(paciente=paciente).order_by('-fecha_autoevaluacion').first()
        if ultima:
            delta = serializer.validated_data.get("fecha_autoevaluacion") or ultima.fecha_autoevaluacion
            dias = (delta - ultima.fecha_autoevaluacion).days
            if dias < 90:
                raise PermissionDenied("Debes esperar al menos 90 días para una nueva autoevaluación.")
        serializer.save(paciente=paciente)


class RespuestaViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet para manejar las respuestas a las preguntas de la autoevaluación MIDAS.
    Permite crear respuestas y listar las respuestas de una autoevaluación específica.
    """
    queryset = Respuesta.objects.select_related('autoevaluacion', 'pregunta').all()
    serializer_class = RespuestaSerializer
    permission_classes = [permissions.IsAuthenticated, EsPaciente]

    def create(self, request, *args, **kwargs):
        """
        Crea una respuesta y, si es la última (pregunta 5), actualiza el puntaje total.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        respuesta = serializer.save()
        autoevaluacion = respuesta.autoevaluacion
        if autoevaluacion.respuestas_midas_individuales.count() == 5:
            # Actualiza el puntaje total y grado de discapacidad
            autoevaluacion.actualizar_puntaje_total()
        return Response(serializer.data)


class EpisodioCefaleaViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet para la gestión de la bitácora de episodios de cefalea.

    Permite a los pacientes registrar sus episodios y a todo el personal
    (paciente, médico, enfermera) visualizar los registros con los
    permisos adecuados.

    Endpoints:
    - POST /api/evaluaciones/episodios/ - Crear un nuevo episodio (Solo Pacientes)
    - GET /api/evaluaciones/episodios/ - Lista los episodios (Paciente ve los suyos, Personal Médico puede filtrar por paciente)
    - GET /api/evaluaciones/episodios/{id}/ - Detalle de un episodio específico
    """
    queryset = EpisodioCefalea.objects.all().select_related('paciente').order_by('-creado_en')

    def get_serializer_class(self):
        """
        Selecciona el serializer adecuado según la acción.
        """
        if self.action == 'create':
            return CrearEpisodioCefaleaSerializer
        return EpisodioCefaleaSerializer

    def get_permissions(self):
        """
        Asigna los permisos adecuados según la acción.
        """
        if self.action == 'create':
            # Solo los pacientes autenticados pueden crear
            return [permissions.IsAuthenticated(), EsPaciente()]

        # Para 'list' y 'retrieve'
        return [permissions.IsAuthenticated(), EsPropietarioDelEpisodioOPersonalMedico()]

    def get_serializer_context(self):
        """
        Inyecta el 'request' en el contexto del serializer.
        Esencial para que el serializer de creación pueda acceder al usuario
        y aplicar la lógica condicional de género.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        """
        Filtra los episodios de manera inteligente según el rol del usuario.
        """
        usuario = self.request.user
        queryset = super().get_queryset()

        # Si el usuario es médico o enfermera
        if usuario.es_medico or usuario.es_enfermera:
            # Pueden filtrar los episodios de un paciente específico usando un query param
            paciente_id = self.request.query_params.get('paciente_id', None)
            if paciente_id:
                return queryset.filter(paciente_id=paciente_id)
            # Si no especifican un paciente, no devolvemos nada para no exponer datos masivos.
            return queryset.none()

            # Si el usuario es paciente, solo puede ver sus propios episodios
        if usuario.es_paciente:
            return queryset.filter(paciente=usuario)

        # En cualquier otro caso, no devolver nada.
        return queryset.none()

    def perform_create(self, serializer):
        """
        Personaliza el proceso de guardado de un nuevo episodio.
        """
        episodio_cefalea_service.registrar_nuevo_episodio(
            paciente=self.request.user,
            datos_validados=serializer.validated_data
        )