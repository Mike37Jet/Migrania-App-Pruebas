# evaluacion_diagnostico/autoevaluacion_midas_service.py
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from usuarios.models import Usuario

from datetime import timedelta


class AutoevaluacionMidasService:
    """
    Servicio para manejar la lógica de negocio relacionada con autoevaluaciones MIDAS.
    """

    MIN_DIAS_ESPERA = 90  # días requeridos entre evaluaciones

    def __init__(self, repository=None):
        """
        Inicializar servicio con repositorio inyectable.
        """
        from .models import AutoevaluacionMidas
        self.autoevaluacion_midas = AutoevaluacionMidas

        # Usar repositorio inyectado o crear uno por defecto
        if repository is None:
            from .repositories import DjangoAutoevaluacionMidasRepository
            self.repository = DjangoAutoevaluacionMidasRepository()
        else:
            self.repository = repository

    def puede_iniciar_autoevaluacion(self, paciente: Usuario, en_fecha) -> bool:
        """
        Verifica si el paciente puede iniciar una nueva evaluación MIDAS.

        Reglas:
        - Si no tiene ninguna evaluación, puede iniciar.
        - Si la última evaluación fue hace 90 días o más, puede iniciar.
        """
        ultima_autoevaluacion = self.repository.obtener_ultima_autoevaluacion(paciente)

        if not ultima_autoevaluacion:
            return True

        ultima_fecha = ultima_autoevaluacion.fecha_autoevaluacion

        hace_tres_meses = en_fecha - timedelta(days=self.MIN_DIAS_ESPERA)

        return ultima_fecha <= hace_tres_meses

    @transaction.atomic
    def iniciar_autoevaluacion_para(self, paciente: Usuario, en_fecha):
        """
        Crea una nueva autoevaluación MIDAS.
        """
        nueva_autoevaluacion = None
        if not paciente.es_paciente:
            raise ValidationError("Solo los pacientes pueden realizar autoevaluaciones MIDAS.")

        if en_fecha is None:
            fecha_actual = timezone.now().date()
        else:
            fecha_actual = en_fecha.date() if hasattr(en_fecha, 'date') else en_fecha

        if self.puede_iniciar_autoevaluacion(paciente, en_fecha=fecha_actual):
            nueva_autoevaluacion = self.repository.crear_autoevaluacion(paciente, fecha_actual)

        return nueva_autoevaluacion


#  Instanciar servicio
autoevaluacion_midas_service = AutoevaluacionMidasService()
