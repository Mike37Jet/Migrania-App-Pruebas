# usuarios/serializers.py
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import MedicoProfile, PacienteProfile, EnfermeraProfile
from .services import usuario_service
from datetime import date

Usuario = get_user_model()

class MedicoProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicoProfile
        fields = '__all__'
        extra_kwargs = {'usuario': {'read_only': True}}

class PacienteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteProfile
        fields = '__all__'
        extra_kwargs = {'usuario': {'read_only': True}}

class EnfermeraProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnfermeraProfile
        fields = '__all__'
        extra_kwargs = {'usuario': {'read_only': True}}

class UsuarioCompletoSerializer(BaseUserSerializer):
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    edad = serializers.ReadOnlyField()
    perfil_medico = MedicoProfileSerializer(read_only=True)
    perfil_paciente = PacienteProfileSerializer(read_only=True)
    perfil_enfermera = EnfermeraProfileSerializer(read_only=True)
    
    class Meta(BaseUserSerializer.Meta):
        model = Usuario
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'nombre_completo',
            'cedula', 'telefono', 'fecha_nacimiento', 'edad', 'direccion', 'genero',
            'tipo_usuario', 'date_joined', 'creado_en',
            'perfil_medico', 'perfil_paciente', 'perfil_enfermera'
        )

# =================================================
# SERIALIZERS DE REGISTRO ESPECÍFICOS
# =================================================

class RegistroMedicoSerializer(BaseUserCreateSerializer):
    # Campos del perfil médico
    numero_licencia = serializers.CharField(max_length=50)
    especializacion = serializers.CharField(max_length=100)
    anos_experiencia = serializers.IntegerField()
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = Usuario
        fields = (
            'email', 'username', 'password',
            'first_name', 'last_name', 'cedula', 'telefono', 'fecha_nacimiento',
            'direccion', 'genero',
            'numero_licencia', 'especializacion', 'anos_experiencia',
        )
    
    def validate(self, attrs):
        # Separar datos del usuario y del perfil
        perfil_data = {
            'numero_licencia': attrs.pop('numero_licencia'),
            'especializacion': attrs.pop('especializacion'),
            'anos_experiencia': attrs.pop('anos_experiencia')
        }
        
        # Validar datos base del usuario con DRF
        validated_attrs = super().validate(attrs)
        
        # Almacenar datos del perfil para usar en create()
        validated_attrs['_perfil_data'] = perfil_data
        
        return validated_attrs

    def create(self, validated_data):
        # Extraer datos del perfil
        perfil_data = validated_data.pop('_perfil_data')
        
        # Usar el servicio para crear el médico
        try:
            usuario = usuario_service.crear_medico(validated_data, perfil_data)
            return usuario
        except ValidationError as e:
            # Convertir ValidationError de Django a errores de DRF
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(e.error_dict)
            else:
                raise serializers.ValidationError({'error': str(e)})

class RegistroPacienteSerializer(BaseUserCreateSerializer):
    # Campos del perfil paciente
    numero_seguro = serializers.CharField(max_length=50, required=False, allow_blank=True)
    contacto_emergencia_nombre = serializers.CharField(max_length=100)
    contacto_emergencia_telefono = serializers.CharField(max_length=15)
    contacto_emergencia_relacion = serializers.CharField(max_length=50)
    alergias = serializers.CharField(required=False, allow_blank=True)
    grupo_sanguineo = serializers.CharField(max_length=5, required=False, allow_blank=True)
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = Usuario
        fields = (
            'email', 'username', 'password',
            'first_name', 'last_name', 'cedula', 'telefono', 'fecha_nacimiento',
            'direccion', 'genero',
            'numero_seguro', 'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'contacto_emergencia_relacion', 'alergias', 'grupo_sanguineo'
        )

    def validate(self, attrs):
        # Separar datos del usuario y del perfil
        perfil_data = {
            'numero_seguro': attrs.pop('numero_seguro', ''),
            'contacto_emergencia_nombre': attrs.pop('contacto_emergencia_nombre'),
            'contacto_emergencia_telefono': attrs.pop('contacto_emergencia_telefono'),
            'contacto_emergencia_relacion': attrs.pop('contacto_emergencia_relacion'),
            'alergias': attrs.pop('alergias', ''),
            'grupo_sanguineo': attrs.pop('grupo_sanguineo', '')
        }
        
        # Validar datos base del usuario con DRF
        validated_attrs = super().validate(attrs)
        
        # Almacenar datos del perfil para usar en create()
        validated_attrs['_perfil_data'] = perfil_data
        
        return validated_attrs

    def create(self, validated_data):
        # Extraer datos del perfil
        perfil_data = validated_data.pop('_perfil_data')
        
        # Usar el servicio para crear el paciente
        try:
            usuario = usuario_service.crear_paciente(validated_data, perfil_data)
            return usuario
        except ValidationError as e:
            # Convertir ValidationError de Django a errores de DRF
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(e.error_dict)
            else:
                raise serializers.ValidationError({'error': str(e)})

class RegistroEnfermeraSerializer(BaseUserCreateSerializer):
    # Campos del perfil enfermera
    numero_registro = serializers.CharField(max_length=50)
    departamento = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = Usuario
        fields = (
            'email', 'username', 'password',
            'first_name', 'last_name', 'cedula', 'telefono', 'fecha_nacimiento',
            'direccion', 'genero',
            'numero_registro', 'departamento'
        )

    def validate(self, attrs):
        # Separar datos del usuario y del perfil
        perfil_data = {
            'numero_registro': attrs.pop('numero_registro'),
            'departamento': attrs.pop('departamento', '')
        }
        
        # Validar datos base del usuario con DRF
        validated_attrs = super().validate(attrs)
        
        # Almacenar datos del perfil para usar en create()
        validated_attrs['_perfil_data'] = perfil_data
        
        return validated_attrs

    def create(self, validated_data):
        # Extraer datos del perfil
        perfil_data = validated_data.pop('_perfil_data')
        
        # Usar el servicio para crear la enfermera
        try:
            usuario = usuario_service.crear_enfermera(validated_data, perfil_data)
            return usuario
        except ValidationError as e:
            # Convertir ValidationError de Django a errores de DRF
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(e.error_dict)
            else:
                raise serializers.ValidationError({'error': str(e)})

# =================================================
# OTROS SERIALIZERS
# =================================================

class MedicoCompletoSerializer(serializers.ModelSerializer):
    usuario = UsuarioCompletoSerializer(read_only=True)
    
    class Meta:
        model = MedicoProfile
        fields = '__all__'

class PacienteCompletoSerializer(serializers.ModelSerializer):
    usuario = UsuarioCompletoSerializer(read_only=True)
    
    class Meta:
        model = PacienteProfile
        fields = '__all__'

class EnfermeraCompletoSerializer(serializers.ModelSerializer):
    usuario = UsuarioCompletoSerializer(read_only=True)
    
    class Meta:
        model = EnfermeraProfile
        fields = '__all__'

# Serializer base para creación general
class CrearUsuarioSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = Usuario
        fields = (
            'email', 'username', 'password',
            'first_name', 'last_name', 'cedula', 'telefono', 'fecha_nacimiento',
            'direccion', 'genero', 'tipo_usuario'
        )
