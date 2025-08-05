# analiticas/services.py
from collections import Counter
from typing import List, Dict
from .repositories import FakeAnalisisPatronesRepository


class AnalisisPatronesService:
    """
    Contiene la lógica de negocio para analizar los patrones
    en la bitácora de episodios de un paciente.
    """

    def __init__(self, repository: FakeAnalisisPatronesRepository):
        self.repository = repository

    def _es_afirmativo(self, valor):
        """Función de ayuda robusta para verificar si un valor es afirmativo."""
        return str(valor).lower() in ['sí', 'si', 'true']

    def analizar_patrones_clinicos(self, paciente_id: int) -> str:
        """
        Analiza las características clave. Si hay pocos datos, los describe.
        Si hay suficientes, busca patrones estadísticos.
        """
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        if not episodios:
            return "Aún no has registrado ningún episodio. ¡Empieza tu bitácora para descubrir tus patrones!"

        # Modo Descriptivo para nuevos usuarios
        if len(episodios) < 5:
            ultimo = episodios[0]
            loc = ultimo.localizacion.lower() if ultimo.localizacion else 'no especificada'
            car = ultimo.caracter_dolor.lower() if ultimo.caracter_dolor else 'no especificado'
            act = "se agravó con la actividad" if ultimo.empeora_actividad else "no se agravó con la actividad"
            return (f"Tu último episodio tuvo una localización {loc}, fue de carácter {car} y {act}. "
                    "Registra al menos 5 episodios para que podamos detectar patrones.")

        # Modo Estadístico para usuarios con historial
        total = len(episodios)
        loc_counts = Counter(e.localizacion for e in episodios)
        car_counts = Counter(e.caracter_dolor for e in episodios)
        act_counts = Counter(e.empeora_actividad for e in episodios)

        loc_mas_comun, freq_loc = loc_counts.most_common(1)[0]
        car_mas_comun, freq_car = car_counts.most_common(1)[0]

        if (freq_loc / total >= 0.7 and
                freq_car / total >= 0.7 and
                act_counts.get(True, 0) / total > 0.6):

            if loc_mas_comun == "Unilateral" and car_mas_comun == "Pulsátil":
                return ("Se ha detectado un patrón clínico muy consistente. Tus episodios casi siempre son "
                        "unilaterales, de carácter pulsátil y se agravan con la actividad física. "
                        "Estas son características típicas de la migraña.")

        return "Aún no se ha detectado un patrón clínico dominante. Sigue registrando tus episodios para un análisis más preciso."

    def analizar_frecuencia_sintomas(self, paciente_id: int) -> Dict[str, str]:
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        if not episodios:
            return {}

        conclusiones = {}
        sintomas = []
        for e in episodios:
            if e.nauseas_vomitos: sintomas.append("náuseas y/o vómitos")
            if e.fotofobia: sintomas.append("fotofobia (sensibilidad a la luz)")
            if e.fonofobia: sintomas.append("fonofobia (sensibilidad al sonido)")

        if sintomas:
            sintoma_frecuente, freq = Counter(sintomas).most_common(1)[0]
            if len(episodios) < 5:
                conclusiones['sintoma_frecuente'] = f"En tu último episodio experimentaste {sintoma_frecuente}."
            else:
                if "fonofobia" in sintoma_frecuente:
                    conclusiones[
                        'sintoma_frecuente'] = "Se observa que la fonofobia (sensibilidad al sonido) es un síntoma constante en tus crisis."

        episodios_severos = [e for e in episodios if e.severidad == "Severa"]
        if episodios_severos:
            nauseas_en_severos = sum(1 for e in episodios_severos if e.nauseas_vomitos)
            if (nauseas_en_severos / len(episodios_severos) >= 0.5):
                conclusiones['correlacion_severidad'] = (
                    "Parece haber una relación entre la intensidad del dolor y las náuseas: "
                    "cuando la cefalea es 'Severa', es más probable que experimentes náuseas.")
        return conclusiones

    def analizar_patrones_aura(self, paciente_id: int) -> str:
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        if not episodios:
            return "No hay datos de episodios para analizar el aura."

        episodios_con_aura = [e for e in episodios if e.presencia_aura]

        if not episodios_con_aura:
            return "En tu historial no se han registrado episodios con aura."

        # Modo Descriptivo
        if len(episodios) < 5:
            ultimo_aura = episodios_con_aura[0]
            tipo_aura = ultimo_aura.sintomas_aura.lower()
            duracion = ultimo_aura.duracion_aura_minutos
            return f"En tu último episodio con aura, los síntomas fueron de tipo {tipo_aura} y duraron {duracion} minutos."

        # Modo Estadístico
        tipos_aura_set = {e.sintomas_aura.lower() for e in episodios_con_aura if
                          e.sintomas_aura and e.sintomas_aura != "Ninguno"}
        tipos_str = "visual (o sensorial)" if "visuales" in tipos_aura_set and "sensoriales" in tipos_aura_set else " o ".join(
            sorted(list(tipos_aura_set)))

        duraciones = [int(e.duracion_aura_minutos) for e in episodios_con_aura]
        min_dur, max_dur = min(duraciones), max(duraciones)

        return (f"Tu bitácora muestra que experimentas dos tipos de crisis: migrañas sin aura y migrañas con aura. "
                f"Cuando tienes un aura, suele ser de tipo {tipos_str} y durar aproximadamente entre {min_dur} y {max_dur} minutos.")

    def analizar_recurrencia_semanal(self, paciente_id: int) -> List[str]:
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        if not episodios:
            return []

        dias_semana = [e.dia for e in episodios if e.dia]

        counts = Counter(dias_semana)
        dias_recurrentes_set = {dia for dia, count in counts.items() if count > 1}

        orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dias_recurrentes_ordenados = sorted(list(dias_recurrentes_set),
                                            key=lambda x: orden_dias.index(x) if x in orden_dias else 99)

        return dias_recurrentes_ordenados

    def analizar_patron_menstrual(self, paciente_id: int) -> str:
        episodios = self.repository.obtener_episodios_por_paciente(paciente_id)
        if not episodios:
            return "No hay datos para analizar patrones menstruales."

        episodios_menstruales = [e for e in episodios if e.en_menstruacion]

        if not episodios_menstruales:
            return "En tu historial no se han registrado episodios durante la menstruación."

        migranas_menstruales = sum(1 for e in episodios_menstruales if "Migraña" in e.categoria_diagnostica)

        if len(episodios) < 5:
            return "Se ha detectado un episodio durante tu menstruación. Sigue registrando para ver si se trata de un patrón."

        if episodios_menstruales and (migranas_menstruales / len(episodios_menstruales) > 0.7):
            return (
                "Hemos detectado que una parte significativa de tus episodios de migraña ocurren durante tu menstruación. "
                "Esto podría indicar un patrón de 'migraña menstrual'. Te recomendamos conversar sobre este patrón con tu médico.")

        return "No se ha detectado un patrón claro de migraña menstrual en tu historial."
