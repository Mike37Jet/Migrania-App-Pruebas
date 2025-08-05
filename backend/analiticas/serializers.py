# analiticas/serializers.py
from rest_framework import serializers

class AnalisisPatronesSerializer(serializers.Serializer):
    """
    Serializador para empaquetar todas las conclusiones del análisis.
    """
    conclusion_clinica = serializers.CharField()
    conclusiones_sintomas = serializers.DictField()
    conclusion_aura = serializers.CharField()
    dias_recurrentes = serializers.ListField(child=serializers.CharField())
    conclusion_hormonal = serializers.CharField()