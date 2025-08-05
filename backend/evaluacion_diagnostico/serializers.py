from rest_framework import serializers
from .models import AutoevaluacionMidas, Pregunta, Respuesta, EpisodioCefalea
from rest_framework import serializers
from usuarios.models import Usuario


class PreguntaSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar las preguntas de la autoevaluación MIDAS.
    """

    class Meta:
        model = Pregunta
        fields = ['id', 'orden_pregunta', 'enunciado_pregunta']
        read_only_fields = ['id']


class CrearAutoevaluacionSerializer(serializers.ModelSerializer):
    """
    Serializer para crear una autoevaluación MIDAS.
    Permite que un paciente cree una nueva autoevaluación MIDAS.
    """

    class Meta:
        model = AutoevaluacionMidas
        fields = ['id', 'paciente', 'fecha_autoevaluacion']
        read_only_fields = ['id', 'paciente', 'fecha_autoevaluacion']


class CrearRespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = ['autoevaluacion', 'pregunta', 'valor_respuesta']

    # TODO: revisar redundancia
    def validate(self, data):
        evaluacion = data.get('autoevaluacion')
        if evaluacion.respuestas_midas_individuales.count() >= 5:
            raise serializers.ValidationError("No se pueden registrar más de 5 respuestas.")
        return data


class RespuestaSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar las respuestas a las preguntas de la autoevaluación MIDAS.
    Permite ver las respuestas registradas en la autoevaluación MIDAS.
    """

    pregunta = PreguntaSerializer(read_only=True)

    class Meta:
        model = Respuesta
        fields = ['pregunta', 'valor_respuesta', 'respondido_en']


class AutoevaluacionMidasSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar los detalles de una autoevaluación MIDAS.
    Incluye el puntaje total, grado de discapacidad y las respuestas individuales.
    """

    respuestas_midas_individuales = RespuestaSerializer(many=True, read_only=True)

    class Meta:
        model = AutoevaluacionMidas
        fields = ['id', 'fecha_autoevaluacion',
                  'puntaje_total', 'grado_discapacidad',
                  'respuestas_midas_individuales']


class CrearEpisodioCefaleaSerializer(serializers.ModelSerializer):
    """
    Serializer para que un paciente pueda registrar un nuevo episodio de cefalea.
    Se encarga de las validaciones de entrada y de la lógica condicional
    para campos relacionados con el género femenino.
    """

    class Meta:
        model = EpisodioCefalea
        # Campos que el paciente puede enviar al crear un episodio.
        # 'paciente' y 'categoria_diagnostica' se asignarán automáticamente.
        fields = [
            'duracion_cefalea_horas', 'severidad', 'localizacion', 'caracter_dolor',
            'empeora_actividad', 'nauseas_vomitos', 'fotofobia', 'fonofobia',
            'presencia_aura', 'sintomas_aura', 'duracion_aura_minutos',
            'en_menstruacion', 'anticonceptivos'
        ]
        # Hacemos los campos de género femenino opcionales por defecto
        extra_kwargs = {
            'sintomas_aura': {'required': False, 'allow_blank': True},
            'en_menstruacion': {'required': False},
            'anticonceptivos': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        """
        Sobrescribe el constructor para acceder al usuario (paciente)
        y así poder ocultar campos dinámicamente.
        """
        super().__init__(*args, **kwargs)

        # Obtenemos el usuario del contexto, que será inyectado desde la vista.
        usuario = self.context.get('request').user

        # Si el usuario no es de género Femenino, eliminamos los campos
        # para que no aparezcan en la API (ni en la UI que la consuma).
        if not (usuario and usuario.is_authenticated and usuario.genero == Usuario.Genero.FEMENINO):
            if 'en_menstruacion' in self.fields:
                del self.fields['en_menstruacion']
            if 'anticonceptivos' in self.fields:
                del self.fields['anticonceptivos']


class EpisodioCefaleaSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para mostrar la lista resumida y el detalle
    de los episodios de cefalea.
    """
    # Para mostrar el nombre en lugar del ID
    paciente = serializers.StringRelatedField()

    class Meta:
        model = EpisodioCefalea
        # Exponemos todos los campos relevantes para la visualización.
        # No hay riesgo porque es de solo lectura.
        fields = [
            'id', 'paciente', 'creado_en', 'categoria_diagnostica',
            'duracion_cefalea_horas', 'severidad', 'localizacion', 'caracter_dolor',
            'empeora_actividad', 'nauseas_vomitos', 'fotofobia', 'fonofobia',
            'presencia_aura', 'sintomas_aura', 'duracion_aura_minutos',
            'en_menstruacion', 'anticonceptivos'
        ]
