# evaluacion_diagnostico/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from usuarios.models import Usuario
from django.core.exceptions import ValidationError

class AutoevaluacionMidas(models.Model):
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='autoevaluaciones_midas',
                                 limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.PACIENTE},
                                 verbose_name='Paciente')
    fecha_autoevaluacion = models.DateField(auto_now_add=True, verbose_name='Fecha de la autoevaluación')
    puntaje_total = models.PositiveIntegerField(default=0, verbose_name='Puntaje Total',
                                                help_text='Puntaje total de la autoevaluación MIDAS')

    GRADO_DISCAPACIDAD_CHOICES = [
        ('I', 'Grado I - Discapacidad mínima'),
        ('II', 'Grado II - Discapacidad leve'),
        ('III', 'Grado III - Discapacidad moderada'),
        ('IV', 'Grado IV - Discapacidad severa'),
    ]

    grado_discapacidad = models.CharField(
        max_length=5,
        choices=GRADO_DISCAPACIDAD_CHOICES,
        blank=True,
        verbose_name='Grado de Discapacidad'
    )

    class Meta:
        db_table = 'evaluacion_midas'
        ordering = ['-fecha_autoevaluacion']
        unique_together = ('paciente', 'fecha_autoevaluacion')
        verbose_name = 'Evaluación MIDAS'
        verbose_name_plural = 'Evaluaciones MIDAS'
        indexes = [
            models.Index(fields=['paciente', 'fecha_autoevaluacion'])
        ]

    def __str__(self):
        return f"{self.paciente.nombre_completo} - {self.fecha_autoevaluacion}"

    def calcular_puntaje_total(self):
        """
        Calcula el puntaje total de la autoevaluación MIDAS sumando los valores de las respuestas.
        Si no hay respuestas, retorna 0.
        """
        return self.respuestas_midas_individuales.aggregate(
            total=models.Sum('valor_respuesta')
        )['total'] or 0

    def actualizar_puntaje_total(self):
        """
        Actualiza el puntaje total de la autoevaluación MIDAS.
        Llama al método calcular_puntaje_total y guarda el resultado en el campo puntaje_total.
        """
        self.puntaje_total = self.calcular_puntaje_total()
        self.grado_discapacidad = self.calcular_grado_discapacidad()
        self.save(update_fields=['puntaje_total', 'grado_discapacidad'])

    def calcular_grado_discapacidad(self):
        puntaje = self.calcular_puntaje_total()

        if puntaje <= 5:
            return 'I'
        elif puntaje <= 10:
            return 'II'
        elif puntaje <= 20:
            return 'III'
        else:
            return 'IV'


class Pregunta(models.Model):
    """
    Modelo para registrar las preguntas de la autoevaluación MIDAS.

    Contiene las preguntas de la evaluación, similar a una enumeración.
    """
    enunciado_pregunta = models.TextField(verbose_name='Enunciado de la Pregunta')
    orden_pregunta = models.PositiveIntegerField(unique=True, verbose_name='Orden de la Pregunta')

    # Auditoría - Solo fecha de creación según convenciones
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evaluacion_pregunta'
        ordering = ['orden_pregunta']
        verbose_name = 'Pregunta de la autoevaluacion MIDAS'
        verbose_name_plural = 'Preguntas de la autoevaluacion MIDAS'

    def __str__(self):
        """
        Representación en string de la pregunta.
        """
        return f"Pregunta N.{self.orden_pregunta}: {self.enunciado_pregunta}"


class Respuesta(models.Model):
    """
    Modelo para registrar las respuestas a las preguntas de la evaluación MIDAS.
    Cada respuesta está asociada a una evaluación MIDAS y una pregunta específica.
    Permite registrar el valor de la respuesta y la fecha en que fue respondida.
    """
    autoevaluacion = models.ForeignKey(
        AutoevaluacionMidas,
        on_delete=models.CASCADE,
        related_name='respuestas_midas_individuales',
        verbose_name='Evaluación MIDAS'
    )

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='respuesta_a_pregunta',
        verbose_name='Pregunta'
    )

    valor_respuesta = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)],
                                                       verbose_name='Valor de la Pregunta',
                                                       help_text='Número de días, debe estar entre 0 y 90.')

    # Auditoria - Fecha en que se respondió la pregunta
    respondido_en = models.DateTimeField(auto_now=True, verbose_name='Fecha de Respuesta')

    class Meta:
        db_table = 'evaluacion_respuesta'
        unique_together = ('autoevaluacion', 'pregunta')  # una respuesta por pregunta en una evaluación
        verbose_name = 'Respuesta MIDAS'
        verbose_name_plural = 'Respuestas MIDAS'

    def __str__(self):
        return (f"Pregunta {self.pregunta.orden_pregunta} - {self.pregunta.enunciado_pregunta} \n "
                f"Respuesta: {self.valor_respuesta}")

class EpisodioCefalea(models.Model):
    """
    Modelo para registrar episodios de cefalea del paciente.

    Permite el registro detallado de características de episodios de cefalea
    para facilitar el diagnóstico médico y seguimiento del paciente.
    Incluye categorización automática basada en criterios médicos estándar.
    """

    # Constantes para choices
    SEVERIDAD_CHOICES = [
        ('Leve', 'Leve'),
        ('Moderada', 'Moderada'),
        ('Severa', 'Severa'),
    ]

    LOCALIZACION_CHOICES = [
        ('Unilateral', 'Unilateral'),
        ('Bilateral', 'Bilateral'),
    ]

    CARACTER_DOLOR_CHOICES = [
        ('Pulsátil', 'Pulsátil'),
        ('Opresivo', 'Opresivo'),
        ('Punzante', 'Punzante'),
    ]

    SINTOMAS_AURA_CHOICES = [
        ('Visuales', 'Visuales'),
        ('Sensitivos', 'Sensitivos'),
        ('De habla o lenguaje', 'De habla o lenguaje'),
        ('Motores', 'Motores'),
        ('Troncoencefálicos', 'Troncoencefálicos'),
        ('Retinianos', 'Retinianos'),
        ('Ninguno', 'Ninguno'),
    ]

    CATEGORIA_CEFALEA_CHOICES = [
        ('Migraña sin aura', 'Migraña sin aura'),
        ('Migraña con aura', 'Migraña con aura'),
        ('Cefalea de tipo tensional', 'Cefalea de tipo tensional'),
    ]

    # Relaciones
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='episodios_cefalea',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.PACIENTE},
        verbose_name='Paciente'
    )

    # Características principales del episodio
    duracion_cefalea_horas = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(72)],
        verbose_name='Duración Cefalea (horas)',
        help_text='Duración del episodio en horas (1-72)'
    )
    severidad = models.CharField(
        max_length=20,
        choices=SEVERIDAD_CHOICES,
        verbose_name='Severidad del Dolor'
    )
    localizacion = models.CharField(
        max_length=20,
        choices=LOCALIZACION_CHOICES,
        verbose_name='Localización del Dolor'
    )
    caracter_dolor = models.CharField(
        max_length=20,
        choices=CARACTER_DOLOR_CHOICES,
        verbose_name='Carácter del Dolor'
    )

    # Síntomas asociados
    empeora_actividad = models.BooleanField(
        verbose_name='Empeora con Actividad',
        help_text='¿El dolor empeora con actividad física?'
    )
    nauseas_vomitos = models.BooleanField(
        verbose_name='Náuseas o Vómitos'
    )
    fotofobia = models.BooleanField(
        verbose_name='Sensibilidad a la Luz'
    )
    fonofobia = models.BooleanField(
        verbose_name='Sensibilidad al Sonido'
    )

    # Datos del aura
    presencia_aura = models.BooleanField(
        verbose_name='Presencia de Aura'
    )
    sintomas_aura = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Síntomas del Aura',
        help_text='Síntomas de aura separados por comas. Ej: Visuales, Sensitivos'
    )
    duracion_aura_minutos = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        verbose_name='Duración del Aura (min)',
        help_text='Duración del aura en minutos (0-120)'
    )

    # Datos específicos para mujeres
    en_menstruacion = models.BooleanField(
        verbose_name='En menstruación',
        help_text='¿El episodio ocurrió durante la menstruación?',
        default=False
    )
    anticonceptivos = models.BooleanField(
        verbose_name='Uso de Anticonceptivos',
        help_text='¿La paciente usa anticonceptivos hormonales?',
        default=False

    )

    # Categorización diagnóstica
    categoria_diagnostica = models.CharField(
        max_length=50,
        choices=CATEGORIA_CEFALEA_CHOICES,
        blank=True,
        verbose_name='Categoría Diagnóstica',
        help_text='Categorización automática basada en criterios médicos'
    )

    # Auditoría - Solo fecha de creación según convenciones
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )

    class Meta:
        verbose_name = 'Episodio de Cefalea'
        verbose_name_plural = 'Episodios de Cefalea'
        db_table = 'evaluacion_episodio_cefalea'
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['paciente']),
            models.Index(fields=['categoria_diagnostica']),
            models.Index(fields=['creado_en']),
            models.Index(fields=['severidad']),
        ]

    def __str__(self):
        """Representación string del episodio"""
        fecha_str = self.creado_en.strftime('%d/%m/%Y') if self.creado_en else 'Sin fecha'
        categoria = self.categoria_diagnostica or 'Sin categorizar'
        return f"{self.paciente.get_full_name()} - {categoria} ({fecha_str})"

    def clean(self):
        """
        Validaciones de integridad a nivel de modelo.
        """
        super().clean()

        # Validar coherencia de datos de aura
        if self.presencia_aura and self.duracion_aura_minutos == 0:
            raise ValidationError({
                'duracion_aura_minutos': 'Si hay presencia de aura, la duración debe ser mayor a 0.'
            })

        if not self.presencia_aura and self.duracion_aura_minutos > 0:
            raise ValidationError({
                'duracion_aura_minutos': 'Si no hay aura, la duración debe ser 0.'
            })

    @property
    def sintomas_aura_list(self):
        """
        Convierte string de síntomas a lista para facilitar procesamiento
        
        Returns:
            list: Lista de síntomas de aura
        """
        if not self.sintomas_aura or self.sintomas_aura.lower() == 'ninguno':
            return []
        return [s.strip() for s in self.sintomas_aura.split(',') if s.strip()]