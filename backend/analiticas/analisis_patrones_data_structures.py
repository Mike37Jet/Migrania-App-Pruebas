# analiticas/analisis_patrones_data_structures.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

def _to_bool(value: str) -> bool:
    return str(value).lower() in ['sí', 'si', 'true']

@dataclass
class EpisodioData:
    """
    Una clase de datos para representar la información de un episodio de cefalea.
    """
    localizacion: Optional[str] = None
    caracter_dolor: Optional[str] = None
    empeora_actividad: bool = False
    severidad: Optional[str] = None
    nauseas_vomitos: bool = False
    fotofobia: bool = False
    fonofobia: bool = False
    presencia_aura: bool = False
    sintomas_aura: Optional[str] = 'Ninguno'
    duracion_aura_minutos: int = 0
    duracion_cefalea_horas: float = 0.0
    en_menstruacion: bool = False
    anticonceptivos: bool = False
    categoria_diagnostica: str = 'No especificada'
    dia: Optional[str] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    paciente_id: int = 0

    # Convierte los valores de texto 'Sí'/'No' a booleanos al inicializar
    def __post_init__(self):
        for attr_name in ['empeora_actividad', 'nauseas_vomitos', 'fotofobia',
                          'fonofobia', 'presencia_aura', 'en_menstruacion', 'anticonceptivos']:
            valor_actual = getattr(self, attr_name)
            if isinstance(valor_actual, str):
                setattr(self, attr_name, _to_bool(valor_actual))
