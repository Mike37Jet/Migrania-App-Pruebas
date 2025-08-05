from datetime import datetime, timedelta
from django.utils import timezone
from tratamiento.models import Medicamento, Tratamiento, Recordatorio, Alerta, EstadoNotificacion

class TratamientoService:
    def __init__(self, repository):
        self.repository = repository

    def crear_medicamento(self, nombre, dosis, caracteristica, hora_inicio, frecuencia_horas, duracion_dias):
        """Crear un nuevo medicamento"""
        medicamento = Medicamento(
            nombre=nombre,
            dosis=dosis,
            caracteristica=caracteristica,
            hora_de_inicio=hora_inicio,
            frecuencia_horas=frecuencia_horas,
            duracion_dias=duracion_dias
        )
        return self.repository.save_medicamento(medicamento)

    def crear_tratamiento(self, paciente, episodio=None, recomendaciones=None, fecha_inicio=None, activo=True):
        """Crear un nuevo tratamiento"""
        if fecha_inicio is None:
            fecha_inicio = timezone.now().date()

        tratamiento = Tratamiento(
            paciente=paciente,
            episodio=episodio,
            fecha_inicio=fecha_inicio,
            activo=activo,
            recomendaciones=recomendaciones or []
        )
        return self.repository.save_tratamiento(tratamiento)

    def agregar_medicamento_a_tratamiento(self, tratamiento_id, medicamento):
        """Agregar un medicamento al tratamiento"""
        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return False

        # Si el medicamento no existe, lo guardamos primero
        if not medicamento.id:
            medicamento = self.repository.save_medicamento(medicamento)

        return self.repository.add_medicamento_to_tratamiento(tratamiento_id, medicamento.id)

    def generar_notificaciones(self, tratamiento_id, fecha_actual=None):
        """Generar notificaciones para un tratamiento"""
        if fecha_actual is None:
            fecha_actual = timezone.now().date()

        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return []

        notificaciones = tratamiento.generarNotificaciones(fecha_actual)
        for notificacion in notificaciones:
            if isinstance(notificacion, Recordatorio):
                self.repository.save_recordatorio(notificacion)
            elif isinstance(notificacion, Alerta):
                self.repository.save_alerta(notificacion)

        return notificaciones

    def procesar_notificaciones_pendientes(self, tratamiento_id, ahora=None):
        """Procesar notificaciones pendientes"""
        if ahora is None:
            ahora = timezone.now()

        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return []

        notificaciones_procesadas = tratamiento.procesarNotificacionesPendientes(ahora)

        # Guardar las notificaciones procesadas
        for notificacion in notificaciones_procesadas:
            if isinstance(notificacion, Recordatorio):
                self.repository.save_recordatorio(notificacion)
            elif isinstance(notificacion, Alerta):
                self.repository.save_alerta(notificacion)

        return notificaciones_procesadas

    def confirmar_toma(self, alerta_id, tomado=True, hora_confirmacion=None):
        """Confirmar la toma de un medicamento"""
        if hora_confirmacion is None:
            hora_confirmacion = timezone.now()

        alerta = self.repository.get_alerta_by_id(alerta_id)
        if not alerta:
            return None

        if tomado:
            estado = alerta.confirmarTomado(hora_confirmacion)
        else:
            estado = alerta.confirmarNoTomado()

        self.repository.save_alerta(alerta)
        return estado

    def obtener_proxima_notificacion(self, tratamiento_id, ahora=None):
        """Obtener la próxima notificación a enviar"""
        if ahora is None:
            ahora = timezone.now()

        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return None

        return tratamiento.obtenerSiguienteNotificacion(ahora)

    def generar_recordatorio_recomendacion(self, tratamiento_id, recomendacion, hora_actual=None):
        """Generar un recordatorio de recomendación específico"""
        if hora_actual is None:
            hora_actual = timezone.now()

        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return None

        recordatorio = Recordatorio(
            mensaje=f"Recordatorio de recomendación: {recomendacion}",
            fecha_hora=hora_actual,
            estado=EstadoNotificacion.ACTIVO,
            tratamiento=tratamiento
        )

        return self.repository.save_recordatorio(recordatorio)

    def obtener_siguiente_alerta(self, tratamiento_id, ahora=None):
        """Obtener la siguiente alerta pendiente de un tratamiento"""
        if ahora is None:
            ahora = timezone.now()

        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return None

        # Buscar la siguiente alerta activa
        siguiente_alerta = self.repository.get_siguiente_alerta(tratamiento_id, ahora)
        return siguiente_alerta

    def cambiar_estado_alerta(self, alerta_id, nuevo_estado, hora_confirmacion=None):
        """Cambiar el estado de una alerta"""
        if hora_confirmacion is None:
            hora_confirmacion = timezone.now()

        try:
            alerta_id = int(alerta_id)
        except (ValueError, TypeError):
            return None

        alerta = self.repository.get_alerta_by_id(alerta_id)
        if not alerta:
            return None

        if nuevo_estado == EstadoNotificacion.CONFIRMADO_TOMADO:
            estado = alerta.confirmarTomado(hora_confirmacion)
        elif nuevo_estado == EstadoNotificacion.CONFIRMADO_NO_TOMADO:
            estado = alerta.confirmarNoTomado()
        else:
            alerta.asignarEstado(nuevo_estado)
            estado = nuevo_estado

        self.repository.save_alerta(alerta)
        return {
            'alerta_id': alerta_id,
            'estado_anterior': alerta.estado,
            'estado_nuevo': estado,
            'mensaje': alerta.mensaje
        }

    def mostrar_recordatorio(self, recordatorio_id):
        """Mostrar un recordatorio específico"""
        try:
            recordatorio_id = int(recordatorio_id)
        except (ValueError, TypeError):
            return None
            
        recordatorio = self.repository.get_recordatorio_by_id(recordatorio_id)
        if not recordatorio:
            return None

        # Marcar como enviado si está activo
        if recordatorio.estado == EstadoNotificacion.ACTIVO:
            enviado = recordatorio.enviar()
            self.repository.save_recordatorio(recordatorio)
            return {
                'recordatorio_id': recordatorio_id,
                'mensaje': recordatorio.mensaje,
                'fecha_hora': recordatorio.fecha_hora,
                'estado': recordatorio.estado,
                'enviado': enviado
            }

        return {
            'recordatorio_id': recordatorio_id,
            'mensaje': recordatorio.mensaje,
            'fecha_hora': recordatorio.fecha_hora,
            'estado': recordatorio.estado,
            'enviado': False
        }

    def desactivar_recordatorio(self, recordatorio_id):
        """Desactivar un recordatorio"""
        try:
            recordatorio_id = int(recordatorio_id)
        except (ValueError, TypeError):
            return None
            
        recordatorio = self.repository.get_recordatorio_by_id(recordatorio_id)
        if not recordatorio:
            return None

        # Cambiar estado a uno que indique que está desactivado
        recordatorio.asignarEstado(EstadoNotificacion.CONFIRMADO_NO_TOMADO)
        self.repository.save_recordatorio(recordatorio)

        return {
            'recordatorio_id': recordatorio_id,
            'mensaje': recordatorio.mensaje,
            'estado_anterior': EstadoNotificacion.ACTIVO,
            'estado_nuevo': recordatorio.estado,
            'desactivado': True
        }

    def obtener_notificaciones_pendientes(self, tratamiento_id, ahora=None):
        """Obtener todas las notificaciones pendientes de un tratamiento"""
        if ahora is None:
            ahora = timezone.now()

        tratamiento = self.repository.get_tratamiento_by_id(tratamiento_id)
        if not tratamiento:
            return []

        return tratamiento.obtenerNotificacionesPendientes()
