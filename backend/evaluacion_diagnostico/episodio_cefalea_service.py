# evaluacion_diagnostico/services.py
from typing import Dict, Any, List, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from usuarios.models import Usuario


class EpisodioCefaleaService:
    """
    Servicio para manejar la lógica de negocio de episodios de cefalea.
    """

    def __init__(self, repository=None):
        """
        Inicializar servicio con repositorio inyectable.
        """
        # Importar aquí para evitar dependencias circulares
        from .models import EpisodioCefalea
        self.EpisodioCefalea = EpisodioCefalea

        # Usar repositorio inyectado o crear uno por defecto
        if repository is None:
            from .repositories import DjangoEpisodioCefaleaRepository
            self.repository = DjangoEpisodioCefaleaRepository()
        else:
            self.repository = repository

    def convertir_valor_booleano(self, valor: str) -> bool:
        """Convierte valores de texto a booleano según convenciones médicas."""
        if isinstance(valor, bool):
            return valor

        valor_str = str(valor).lower().strip()
        valores_positivos = ['sí', 'si', 'yes', 'true', '1', 'verdadero', 'cierto']
        return valor_str in valores_positivos

    def procesar_datos_episodio(self, datos_tabla: Dict[str, str]) -> Dict[str, Any]:
        """Procesa datos de tabla BDD a formato del modelo."""
        datos_procesados = {}

        mapeo_campos = {
            'Duración Cefalea (horas)': 'duracion_cefalea_horas',
            'Severidad del Dolor': 'severidad',
            'Localización del Dolor': 'localizacion',
            'Carácter del Dolor': 'caracter_dolor',
            'Empeora con Actividad': 'empeora_actividad',
            'Náuseas o Vómitos': 'nauseas_vomitos',
            'Sensibilidad a la Luz': 'fotofobia',
            'Sensibilidad al Sonido': 'fonofobia',
            'Presencia de Aura': 'presencia_aura',
            'Síntomas del Aura': 'sintomas_aura',
            'Duración del Aura (min)': 'duracion_aura_minutos',
            'En menstruación': 'en_menstruacion',
            'Anticonceptivos': 'anticonceptivos'
        }

        for nombre_caracteristica, valor in datos_tabla.items():
            if nombre_caracteristica in mapeo_campos:
                campo_modelo = mapeo_campos[nombre_caracteristica]
                try:
                    if campo_modelo in ['duracion_cefalea_horas', 'duracion_aura_minutos']:
                        datos_procesados[campo_modelo] = int(valor)
                    elif campo_modelo in ['empeora_actividad', 'nauseas_vomitos', 'fotofobia',
                                          'fonofobia', 'presencia_aura', 'en_menstruacion', 'anticonceptivos']:
                        datos_procesados[campo_modelo] = self.convertir_valor_booleano(valor)
                    elif campo_modelo == 'sintomas_aura':
                        datos_procesados[campo_modelo] = '' if valor.lower() == 'ninguno' else valor
                    else:
                        datos_procesados[campo_modelo] = valor
                except (ValueError, TypeError) as e:
                    raise ValidationError(f"Error procesando campo '{nombre_caracteristica}': {str(e)}")

        return datos_procesados

    def categorizar_episodio(self, episodio_data: Dict[str, Any]) -> str:
        """Lógica de categorización médica basada en criterios IHS/ICHD-3."""
        presencia_aura = episodio_data.get('presencia_aura', False)
        duracion_aura = episodio_data.get('duracion_aura_minutos', 0)
        severidad = episodio_data.get('severidad', '')
        localizacion = episodio_data.get('localizacion', '')
        caracter_dolor = episodio_data.get('caracter_dolor', '')
        empeora_actividad = episodio_data.get('empeora_actividad', False)
        nauseas_vomitos = episodio_data.get('nauseas_vomitos', False)
        fotofobia = episodio_data.get('fotofobia', False)
        fonofobia = episodio_data.get('fonofobia', False)

        # Criterios para Migraña con Aura
        if presencia_aura and duracion_aura > 0:
            if (severidad in ['Moderada', 'Severa'] and
                    localizacion == 'Unilateral' and
                    caracter_dolor == 'Pulsátil' and
                    empeora_actividad and
                    (fotofobia or fonofobia)):
                return 'Migraña con aura'

        # Criterios para Migraña sin Aura
        if (not presencia_aura and
                severidad in ['Moderada', 'Severa'] and
                localizacion == 'Unilateral' and
                caracter_dolor == 'Pulsátil' and
                empeora_actividad and
                (nauseas_vomitos or fotofobia or fonofobia)):
            return 'Migraña sin aura'

        return 'Cefalea de tipo tensional'

    @transaction.atomic
    def registrar_nuevo_episodio(self, paciente: Usuario, datos_validados: dict):
        """
        Registra un nuevo episodio de cefalea con la API Rest
        y garantiza la integridad de los datos.
        """
        # 1. Lógica de negocio: Categorización
        categoria = self.categorizar_episodio(datos_validados)
        datos_validados['categoria_diagnostica'] = categoria

        # 2. Creación de la instancia del modelo
        from .models import EpisodioCefalea
        episodio = EpisodioCefalea(paciente=paciente, **datos_validados)

        # 3. Garantía de integridad: Llama a las validaciones del modelo.
        episodio.full_clean()

        # 4. Persistencia final en la base de datos real.
        episodio.save()

        return episodio

    def crear_episodio(self, paciente: Usuario, datos_episodio: Dict[str, Any]):
        """Crear episodio usando el repositorio inyectado."""
        # Validaciones
        if not paciente.es_paciente:
            raise ValidationError("Solo los pacientes pueden tener episodios de cefalea")

        sintomas_aura = datos_episodio.get('sintomas_aura', '')
        if sintomas_aura and not self.validar_sintomas_aura(sintomas_aura):
            raise ValidationError("Los síntomas de aura contienen valores inválidos")

        # Categorizar automáticamente
        categoria = self.categorizar_episodio(datos_episodio)
        datos_episodio['categoria_diagnostica'] = categoria

        # Crear usando el repositorio
        return self.repository.crear_episodio(paciente, datos_episodio)

    def obtener_episodios_paciente(self, paciente: Usuario):
        """Obtener episodios usando el repositorio."""
        return self.repository.obtener_episodios_paciente(paciente)

    def obtener_ultimo_episodio(self, paciente: Usuario):
        """Obtener último episodio usando el repositorio."""
        return self.repository.obtener_ultimo_episodio(paciente)

    def validar_sintomas_aura(self, sintomas_aura: str) -> bool:
        """Validar síntomas de aura."""
        if not sintomas_aura or sintomas_aura.lower() == 'ninguno':
            return True

        sintomas_validos = [choice[0] for choice in self.EpisodioCefalea.SINTOMAS_AURA_CHOICES]
        sintomas_lista = [s.strip() for s in sintomas_aura.split(',') if s.strip()]

        for sintoma in sintomas_lista:
            if sintoma not in sintomas_validos:
                return False
        return True

# Instancias para usar en la aplicación
episodio_cefalea_service = EpisodioCefaleaService()  # Con repositorio Django por defecto