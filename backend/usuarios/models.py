# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from datetime import date
from .managers import UsuarioManager  # Importar el manager personalizado

class Usuario(AbstractUser):
    """Usuario base con campos comunes para todos los tipos"""
    class TipoUsuario(models.TextChoices):
        MEDICO = 'medico', 'Médico'
        PACIENTE = 'paciente', 'Paciente'
        ENFERMERA = 'enfermera', 'Enfermera'
    
    class Genero(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        OTRO = 'O', 'Otro'
        PREFIERO_NO_DECIR = 'N', 'Prefiero no decir'
    
    # CAMPOS BÁSICOS (TODOS LOS USUARIOS)
    email = models.EmailField(unique=True, verbose_name='Email')
    cedula = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name='Cédula/DNI',
        default='0000000000'  # Valor por defecto
    )
    tipo_usuario = models.CharField(
        max_length=10, 
        choices=TipoUsuario.choices,
        verbose_name='Tipo de Usuario',
        default=TipoUsuario.MEDICO  # Valor por defecto
    )
    telefono = models.CharField(
        max_length=10, 
        verbose_name='Teléfono',
        default='0000000000'  # Valor por defecto
    )
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de Nacimiento',
        default=date(1990, 1, 1)  # Valor por defecto
    )
    direccion = models.TextField(
        verbose_name='Dirección Completa',
        default='Sin dirección'  # Valor por defecto
    )
    genero = models.CharField(
        max_length=1, 
        choices=Genero.choices, 
        verbose_name='Género',
        default=Genero.PREFIERO_NO_DECIR  # Valor por defecto
    )
        
    # AUDITORÍA
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    # CONFIGURACIÓN
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'cedula', 'first_name', 'last_name']
    
    # MANAGER PERSONALIZADO
    objects = UsuarioManager()
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios_usuario'
        indexes = [
            models.Index(fields=['cedula']),
            models.Index(fields=['email']),
            models.Index(fields=['tipo_usuario']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_tipo_usuario_display()}) - {self.cedula}"
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def es_medico(self):
        return self.tipo_usuario == self.TipoUsuario.MEDICO
    
    @property 
    def es_paciente(self):
        return self.tipo_usuario == self.TipoUsuario.PACIENTE
    
    @property
    def es_enfermera(self):
        return self.tipo_usuario == self.TipoUsuario.ENFERMERA
    
    @property
    def edad(self):
        """Calcula la edad basada en fecha de nacimiento"""
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    @property
    def perfil_especifico(self):
        """Retorna el perfil específico según el tipo de usuario"""
        try:
            if self.es_medico:
                return self.perfil_medico
            elif self.es_paciente:
                return self.perfil_paciente
            elif self.es_enfermera:
                return self.perfil_enfermera
        except:
            return None
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

# PERFILES ESPECÍFICOS (TABLAS SEPARADAS)

class MedicoProfile(models.Model):
    """Perfil específico para médicos"""
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_medico'
    )
    numero_licencia = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número de Licencia Médica'
    )
    especializacion = models.CharField(
        max_length=100, 
        verbose_name='Especialización',
        choices=[
            ('neurologia', 'Neurología'),
            ('medicina_general', 'Medicina General'),
            ('medicina_interna', 'Medicina Interna'),
            ('psiquiatria', 'Psiquiatría'),
            ('neurocirugia', 'Neurocirugía'),
            ('otra', 'Otra'),
        ]
    )
    anos_experiencia = models.IntegerField(
        verbose_name='Años de Experiencia'
    )
    
    class Meta:
        verbose_name = 'Perfil Médico'
        verbose_name_plural = 'Perfiles Médicos'
        db_table = 'usuarios_medico_profile'
    
    def __str__(self):
        return f"Dr. {self.usuario.nombre_completo} - {self.especializacion}"

class PacienteProfile(models.Model):
    """Perfil específico para pacientes"""
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_paciente'
    )
    numero_seguro = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='Número de Seguro Médico'
    )
    contacto_emergencia_nombre = models.CharField(
        max_length=100, 
        verbose_name='Nombre Contacto de Emergencia'
    )
    contacto_emergencia_telefono = models.CharField(
        max_length=15, 
        verbose_name='Teléfono Contacto de Emergencia'
    )
    contacto_emergencia_relacion = models.CharField(
        max_length=50, 
        verbose_name='Relación Contacto de Emergencia'
    )
    alergias = models.TextField(
        blank=True, 
        verbose_name='Alergias Conocidas'
    )
    grupo_sanguineo = models.CharField(
        max_length=5, 
        blank=True, 
        verbose_name='Grupo Sanguíneo',
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    medicamentos_actuales = models.TextField(
        blank=True,
        verbose_name='Medicamentos Actuales'
    )
    enfermedades_cronicas = models.TextField(
        blank=True,
        verbose_name='Enfermedades Crónicas'
    )
    
    class Meta:
        verbose_name = 'Perfil Paciente'
        verbose_name_plural = 'Perfiles Pacientes'
        db_table = 'usuarios_paciente_profile'
    
    def __str__(self):
        return f"Paciente: {self.usuario.nombre_completo}"


class EnfermeraProfile(models.Model):
    """Perfil específico para enfermeras"""
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_enfermera'
    )
    numero_registro = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número de Registro Profesional'
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento'
    )
    
    class Meta:
        verbose_name = 'Perfil Enfermera'
        verbose_name_plural = 'Perfiles Enfermeras'
        db_table = 'usuarios_enfermera_profile'
    
    def __str__(self):
        return f"Enfermera: {self.usuario.nombre_completo}"
