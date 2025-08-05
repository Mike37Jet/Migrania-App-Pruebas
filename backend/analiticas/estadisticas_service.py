# analiticas/estadisticas_service.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from usuarios.models import Usuario
from .analisis_patrones_data_structures import EpisodioData


class EstadisticasHistorialService:
    """
    Servicio para manejar la lógica de negocio de estadísticas e historial.
    """

    def __init__(self, repository=None):
        """
        Inicializar servicio con repositorio inyectable.
        """
        # Usar repositorio inyectado o crear uno por defecto
        if repository is None:
            from .repositories import DjangoAnalisisPatronesRepository
            self.repository = DjangoAnalisisPatronesRepository()
        else:
            self.repository = repository

    def calcular_promedio_semanal(self, paciente_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> float:
        """
        Calcula el promedio semanal de episodios entre dos fechas.
        """
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        
        # Filtrar episodios en el rango de fechas
        episodios_en_rango = [
            ep for ep in episodios 
            if fecha_inicio.date() <= ep.fecha_creacion.date() <= fecha_fin.date()
        ]
        
        total_episodios = len(episodios_en_rango)
        
        # Calcular número de semanas en el período
        delta_dias = (fecha_fin.date() - fecha_inicio.date()).days
        semanas = delta_dias / 7.0
        
        if semanas == 0:
            return 0.0
            
        return round(total_episodios / semanas, 1)

    def calcular_duracion_promedio(self, paciente_id: int) -> float:
        """
        Calcula la duración promedio de episodios en horas.
        """
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        
        if not episodios:
            return 0.0
            
        suma_duracion = sum(ep.duracion_cefalea_horas for ep in episodios)
        return round(suma_duracion / len(episodios), 1)

    def calcular_intensidad_promedio(self, paciente_id: int) -> str:
        """
        Calcula la intensidad promedio del dolor.
        """
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        
        if not episodios:
            return "No hay datos"
            
        # Mapeo de severidad a valores numéricos
        valores_severidad = {'Leve': 1, 'Moderada': 2, 'Severa': 3}
        
        suma_severidad = 0
        episodios_validos = 0
        
        for ep in episodios:
            if ep.severidad in valores_severidad:
                suma_severidad += valores_severidad[ep.severidad]
                episodios_validos += 1
        
        if episodios_validos == 0:
            return "No hay datos"
            
        promedio = suma_severidad / episodios_validos
        
        # Convertir de vuelta a texto (usando formas masculinas para compatibilidad con feature)
        if promedio <= 1.5:
            return "Leve"
        elif promedio <= 2.5:
            return "Moderado"  # Cambiado de "Moderada" a "Moderado"
        else:
            return "Severo"   # Cambiado de "Severa" a "Severo"

    def calcular_porcentajes_hormonales(self, paciente_id: int) -> Dict[str, float]:
        """
        Calcula porcentajes de episodios asociados a menstruación y anticonceptivos.
        """
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        
        if not episodios:
            return {"menstruacion": 0.0, "anticonceptivos": 0.0}
            
        total_episodios = len(episodios)
        episodios_menstruacion = sum(1 for ep in episodios if ep.en_menstruacion)
        episodios_anticonceptivos = sum(1 for ep in episodios if ep.anticonceptivos)
        
        porcentaje_menstruacion = round((episodios_menstruacion / total_episodios) * 100, 1)
        porcentaje_anticonceptivos = round((episodios_anticonceptivos / total_episodios) * 100, 1)
        
        return {
            "menstruacion": porcentaje_menstruacion,
            "anticonceptivos": porcentaje_anticonceptivos
        }

    def validar_episodios_minimos(self, paciente_id: int, minimos: int = 3) -> bool:
        """
        Valida que el paciente tenga al menos el número mínimo de episodios.
        """
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        return len(episodios) >= minimos

    def calcular_evolucion_midas(self, promedio_puntuacion: float, puntuacion_actual: float) -> Dict[str, Any]:
        """
        Calcula la evolución de la puntuación MIDAS.
        
        Args:
            promedio_puntuacion: Promedio histórico de puntuaciones MIDAS
            puntuacion_actual: Puntuación más reciente
            
        Returns:
            Dict con variación y tendencia
        """
        variacion = puntuacion_actual - promedio_puntuacion
        
        if variacion < 0:
            tendencia = "Mejorado"
        elif variacion > 0:
            tendencia = "Empeorado"
        else:
            tendencia = "Sin cambios"
            
        return {
            "variacion": variacion,
            "tendencia": tendencia
        }


# Instancia para usar en la aplicación
estadisticas_historial_service = EstadisticasHistorialService()  # Con repositorio Django por defecto
