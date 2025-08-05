# analiticas/estadisticas_serializers.py
from rest_framework import serializers


class EstadisticasHistorialSerializer(serializers.Serializer):
    """
    Serializer para las estadísticas del historial de episodios de bitácora digital.
    """
    # Estadísticas de promedio semanal
    promedio_semanal = serializers.FloatField(
        required=False,
        help_text="Promedio semanal de episodios de migraña"
    )
    
    # Estadísticas de duración promedio
    duracion_promedio = serializers.FloatField(
        required=False,
        help_text="Duración promedio por episodio en horas"
    )
    
    # Estadísticas de intensidad promedio
    intensidad_promedio = serializers.CharField(
        required=False,
        help_text="Intensidad promedio del dolor (Leve, Moderado, Severo)"
    )
    
    # Estadísticas de asociación hormonal
    porcentaje_menstruacion = serializers.FloatField(
        required=False,
        help_text="Porcentaje de episodios durante menstruación"
    )
    porcentaje_anticonceptivos = serializers.FloatField(
        required=False,
        help_text="Porcentaje de episodios asociados a anticonceptivos"
    )
    
    # Información adicional
    total_episodios = serializers.IntegerField(
        required=False,
        help_text="Total de episodios registrados"
    )
    fecha_primer_episodio = serializers.DateField(
        required=False,
        help_text="Fecha del primer episodio registrado"
    )
    fecha_ultimo_episodio = serializers.DateField(
        required=False,
        help_text="Fecha del último episodio registrado"
    )


class PromediaSemanalRequestSerializer(serializers.Serializer):
    """
    Serializer para los parámetros de solicitud de promedio semanal.
    """
    fecha_inicio = serializers.DateField(
        required=False,
        help_text="Fecha de inicio del período a analizar"
    )
    fecha_fin = serializers.DateField(
        required=False,
        help_text="Fecha de fin del período a analizar"
    )
