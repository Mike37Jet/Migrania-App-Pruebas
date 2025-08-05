from django.db import models
# citas/models.py
from django.db import models
from django.core.exceptions import ValidationError
from usuarios.models import Usuario
from datetime import datetime, timedelta


class Cita(models.Model):
    """Modelo para gestionar las citas médicas"""
    class EstadoCita(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADA = 'confirmada', 'Confirmada'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'
        REPROGRAMADA = 'reprogramada', 'Reprogramada'

    # Relaciones
    doctor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='citas_como_doctor',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.MEDICO}
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='citas',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.PACIENTE}
    )

    # Información de la cita
    fecha = models.DateField(verbose_name='Fecha de la cita')
    hora = models.TimeField(verbose_name='Hora de la cita')
    estado = models.CharField(
        max_length=15,
        choices=EstadoCita.choices,
        default=EstadoCita.PENDIENTE,
        verbose_name='Estado'
    )
    urgente = models.BooleanField(default=False, verbose_name='Es urgente')

    # Detalles adicionales
    motivo = models.TextField(blank=True, verbose_name='Motivo de la consulta')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')

    # Auditoría
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        db_table = 'citas_cita'
        unique_together = ['doctor', 'fecha', 'hora']
        indexes = [
            models.Index(fields=['doctor', 'fecha']),
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['fecha', 'hora']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"Cita: {self.paciente.get_full_name()} con Dr. {self.doctor.get_full_name()} - {self.fecha} {self.hora}"

    @property
    def fecha_hora_completa(self):
        """Combina fecha y hora en un datetime"""
        return datetime.combine(self.fecha, self.hora)

    @property
    def puede_cancelarse(self):
        """Verifica si la cita puede cancelarse (24 hrs antes)"""
        ahora = datetime.now()
        fecha_hora_cita = self.fecha_hora_completa
        return fecha_hora_cita - ahora >= timedelta(hours=24)

    @property
    def puede_reprogramarse(self):
        """Verifica si la cita puede reprogramarse"""
        return self.estado in [self.EstadoCita.PENDIENTE, self.EstadoCita.CONFIRMADA] and self.puede_cancelarse

    def clean(self):
        """Validaciones personalizadas"""
        if self.fecha and self.hora:
            fecha_hora = datetime.combine(self.fecha, self.hora)
            if fecha_hora <= datetime.now():
                raise ValidationError('No se pueden agendar citas en el pasado')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Recordatorio(models.Model):
    """Modelo para gestionar recordatorios de citas"""

    class TipoRecordatorio(models.TextChoices):
        CITA_PROXIMA = 'cita_proxima', 'Cita Próxima'

    # Relaciones
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='recordatorios',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.PACIENTE}
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        related_name='recordatorios',
        null=True,
        blank=True
    )

    # Información del recordatorio
    tipo = models.CharField(
        max_length=15,
        choices=TipoRecordatorio.choices,
        default=TipoRecordatorio.CITA_PROXIMA
    )
    fecha = models.DateField(verbose_name='Fecha del recordatorio')
    hora = models.TimeField(verbose_name='Hora del recordatorio')
    mensaje = models.TextField(verbose_name='Mensaje del recordatorio')
    enviado = models.BooleanField(default=False, verbose_name='¿Fue enviado?')

    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    enviado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        db_table = 'citas_recordatorio'
        indexes = [
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['fecha', 'hora']),
            models.Index(fields=['enviado']),
        ]

    def __str__(self):
        return f"Recordatorio para {self.paciente.get_full_name()} - {self.fecha} {self.hora}"

    @property
    def fecha_hora_completa(self):
        """Combina fecha y hora en un datetime"""
        return datetime.combine(self.fecha, self.hora)

    def marcar_como_enviado(self):
        """Marca el recordatorio como enviado"""
        self.enviado = True
        self.enviado_en = datetime.now()
        self.save()


# Enum para discapacidad (usado en los steps)
class Discapacidad(models.TextChoices):
    NINGUNA = 'ninguna', 'Ninguna'
    LEVE = 'leve', 'Leve'
    MODERADA = 'moderada', 'Moderada'
    SEVERA = 'severa', 'Severa'
