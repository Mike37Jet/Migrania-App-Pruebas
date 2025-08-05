# analiticas/repositories.py

from abc import ABC, abstractmethod
from typing import List
from .analisis_patrones_data_structures import EpisodioData
from evaluacion_diagnostico.models import EpisodioCefalea


class AnalisisPatronesRepository(ABC):
    """Interfaz del repositorio."""

    @abstractmethod
    def obtener_episodios_por_paciente(self, paciente_id: int) -> List[EpisodioData]:
        pass

    # Este es el método que tu contrato requiere
    @abstractmethod
    def guardar_episodio(self, paciente_id: int, episodio: EpisodioData):
        pass


# --- Implementación para Pruebas ---
class FakeAnalisisPatronesRepository(AnalisisPatronesRepository):
    def __init__(self):
        self._episodios = {}

    def limpiar_repositorio(self):
        """Limpia todos los episodios del repositorio fake."""
        self._episodios.clear()

    def guardar_episodio(self, paciente_id: int, episodio: EpisodioData):
        if paciente_id not in self._episodios:
            self._episodios[paciente_id] = []
        self._episodios[paciente_id].append(episodio)

    def obtener_episodios_por_paciente(self, paciente_id: int) -> List[EpisodioData]:
        return self._episodios.get(paciente_id, [])


# --- Implementación para Producción ---
class DjangoAnalisisPatronesRepository(AnalisisPatronesRepository):
    """
    Implementación real que interactúa con la base de datos de Django.
    """

    def obtener_episodios_por_paciente(self, paciente_id: int) -> List[EpisodioData]:
        # --- CORRECCIÓN AQUÍ: Cambiamos 'fecha_creacion' por 'creado_en' ---
        episodios_orm = EpisodioCefalea.objects.filter(paciente_id=paciente_id).order_by('-creado_en')[:50]
        episodios_data = []
        for orm_obj in episodios_orm:
            # --- Y TAMBIÉN AQUÍ ---
            data = EpisodioData(
                localizacion=orm_obj.localizacion,
                caracter_dolor=orm_obj.caracter_dolor,
                empeora_actividad=bool(orm_obj.empeora_actividad),  # Aseguramos que sea un booleano
                severidad=orm_obj.severidad,
                nauseas_vomitos=bool(orm_obj.nauseas_vomitos),  # Aseguramos que sea un booleano
                fotofobia=bool(orm_obj.fotofobia),  # Aseguramos que sea un booleano
                fonofobia=bool(orm_obj.fonofobia),  # Aseguramos que sea un booleano
                presencia_aura=bool(orm_obj.presencia_aura),  # Aseguramos que sea un booleano
                sintomas_aura=orm_obj.sintomas_aura,
                duracion_aura_minutos=orm_obj.duracion_aura_minutos,
                duracion_cefalea_horas=float(orm_obj.duracion_cefalea_horas),  # Agregamos el campo que faltaba
                en_menstruacion=bool(orm_obj.en_menstruacion),  # Aseguramos que sea un booleano
                anticonceptivos=bool(orm_obj.anticonceptivos),  # Agregamos el campo que faltaba
                categoria_diagnostica=orm_obj.categoria_diagnostica,
                dia=orm_obj.creado_en.strftime('%A'),
                fecha_creacion=orm_obj.creado_en,
                paciente_id=orm_obj.paciente_id
            )
            episodios_data.append(data)
        return episodios_data

    def guardar_episodio(self, paciente_id: int, episodio: EpisodioData):
        """
        Este repositorio es de solo lectura. Este método no se usa en producción.
        Se implementa solo para cumplir con el contrato de la clase abstracta.
        """
        raise NotImplementedError("El repositorio de análisis es de solo lectura.")
