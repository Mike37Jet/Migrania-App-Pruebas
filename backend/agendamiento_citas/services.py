# citas/services.py
from datetime import date, datetime, time, timedelta
from typing import Dict, Any, List, Optional
from usuarios.repositories import AbstractUserRepository, DjangoUserRepository
from .repositories import AbstractCitaRepository, AbstractRecordatorioRepository, CitaRepository, RecordatorioRepository


class CitaService:
    """Servicio para manejar la lógica de negocio de citas"""

    def __init__(self,
                 cita_repository: AbstractCitaRepository = None,
                 recordatorio_repository: AbstractRecordatorioRepository = None,
                 user_repository: AbstractUserRepository = None):
        self.cita_repository = cita_repository or CitaRepository()
        self.recordatorio_repository = recordatorio_repository or RecordatorioRepository()
        self.user_repository = user_repository or DjangoUserRepository()

    def crear_cita(self, doctor_id: int, paciente_id: int, fecha: str, hora: str,urgente: bool = False,
                    motivo: str = '') -> Dict[str, Any]:
        """Crear una nueva cita con validaciones de negocio"""
        try:
            # Validar que los usuarios existan
            doctor = self.user_repository.get_user_by_id(doctor_id)
            paciente = self.user_repository.get_user_by_id(paciente_id)
            hora = datetime.strptime(hora, '%H:%M').time() if isinstance(hora, str) else hora
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date() if isinstance(fecha, str) else fecha
            if not doctor or not doctor.es_medico:
                return {'success': False, 'error': 'Doctor no encontrado o no válido'}

            if not paciente or not paciente.es_paciente:
                return {'success': False, 'error': 'Paciente no encontrado o no válido'}

            # Validar disponibilidad del doctor
            if not self.esta_disponibilidad_doctor(paciente_id, fecha, hora):
                return {'success': False, 'error': 'El doctor no está disponible en ese horario'}
            # Validar que no sea en el pasado
            fecha_hora_cita = datetime.combine(fecha, hora)
            if fecha_hora_cita <= datetime.now():
                return {'success': False, 'error': 'No se pueden agendar citas en el pasado'}
            # Crear la cita
            cita_data = {
                'doctor': doctor,
                'paciente': paciente,
                'fecha': fecha,
                'hora': hora,
                'urgente': urgente,
                'motivo': motivo,
                'estado': 'pendiente'
            }

            cita = self.cita_repository.create_cita(cita_data)
            return {
                'success': True,
                'cita': cita,
                'mensaje': 'Cita creada exitosamente'
            }

        except Exception as e:
            return {'success': False, 'error': f'Error al crear la cita: {str(e)}'}

    def esta_disponibilidad_doctor(self, doctor_id: int, fecha: str, hora: str) -> bool:
        """Verificar si un doctor está disponible en una fecha y hora específicas"""
        # Obtener citas existentes del doctor en esa fecha y hora
        hora = datetime.strptime(hora, '%H:%M').time() if isinstance(hora, str) else hora
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date() if isinstance (fecha, str) else fecha
        citas_existentes = self.cita_repository.get_citas_by_doctor_fecha(doctor_id, fecha)

        # Verificar si ya tiene una cita a esa hora
        if citas_existentes is not None:
            for cita in citas_existentes:
                if cita.hora == hora and cita.estado in ['pendiente', 'confirmada']:
                    return False
        else:
            return True

        return True
    def crear_cita_urgente(self,paciente_id: int) -> Dict[str, Any]:
        """Crear una cita urgente para el día actual"""
        try:
            paciente = self.user_repository.get_user_by_id(paciente_id)
            fecha_actual = date.today().strftime("%Y-%m-%d")
            hora_actual = datetime.now()
            hora_exacta= time(hour=hora_actual.hour, minute=0).strftime("%H:%M")
            # Buscar un doctor disponible
            doctores_disponibles = self.obtener_doctores_disponibles(fecha_actual,hora_exacta)
            if not doctores_disponibles:
                return {'success': False, 'error': 'No hay doctores disponibles'}
            # Tomar el primer doctor disponible
            doctor = doctores_disponibles[0]
            hora = datetime.strptime(hora_exacta, '%H:%M').time() if isinstance(hora_exacta, str) else hora_exacta
            fecha = datetime.strptime(fecha_actual, '%Y-%m-%d').date() if isinstance(fecha_actual, str) else fecha_actual
            cita_data = {
                'doctor': doctor,
                'paciente':paciente,
                'fecha': fecha,
                'hora': hora,
                'urgente': True,
                'motivo': 'Atención médica urgente',
                'estado': 'pendiente'
            }
            cita_urgente_agendada = self.cita_repository.create_cita(cita_data)
            return {
                'success': True,
                'cita': cita_urgente_agendada,
                'mensaje': 'Cita creada exitosamente'
            }

        except Exception as e:
            return {'success': False, 'error': f'Error al crear cita urgente: {str(e)}'}


    def obtener_horarios_disponibles(self, doctor_id: int, fecha: str) -> List[str]:
        """Obtener lista de horarios disponibles para un doctor en una fecha"""
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date() if isinstance(fecha, str) else fecha
        horarios_base = [
            '08:00', '09:00', '10:00', '11:00',
            '14:00', '15:00', '16:00', '17:00','18:00','19:00', '20:00'
        ]

        # Obtener citas ocupadas
        citas_ocupadas = self.cita_repository.get_citas_by_doctor_fecha(doctor_id, fecha)
        if citas_ocupadas is None:
            return horarios_base
        horarios_ocupados = [cita.hora.strftime('%H:%M') for cita in citas_ocupadas
                             if cita.estado in ['pendiente', 'confirmada']]

        # Filtrar horarios disponibles
        return [h for h in horarios_base if h not in horarios_ocupados]

    def reprogramar_cita(self, cita_id: int, nueva_fecha: str, nueva_hora: str) -> Dict[str, Any]:
        """Reprogramar una cita existente"""
        try:
            nueva_fecha = datetime.strptime(nueva_fecha, '%Y-%m-%d').date() if isinstance(nueva_fecha, str) else nueva_fecha
            nueva_hora = datetime.strptime(nueva_hora, '%H:%M').time() if isinstance(nueva_hora, str) else nueva_hora
            cita = self.cita_repository.get_cita_by_id(cita_id)
            if not cita:
                return {'success': False, 'error': 'Cita no encontrada'}

            # Validar que se puede reprogramar (24 horas antes)
            if hasattr(cita, 'puede_reprogramarse') and not cita.puede_reprogramarse:
                return {'success': False, 'error': 'La cita no puede reprogramarse (menos de 24 horas)'}

            # Validar disponibilidad en el nuevo horario
            if not self.esta_disponibilidad_doctor(cita.doctor.id, nueva_fecha, nueva_hora):
                return {'success': False, 'error': 'El doctor no está disponible en el nuevo horario'}

            # Actualizar la cita
            datos_actualizacion = {
                'fecha': nueva_fecha,
                'hora': nueva_hora,
                'estado': 'reprogramada'
            }

            cita_actualizada = self.cita_repository.update_cita(cita_id, datos_actualizacion)

            return {
                'success': True,
                'cita': cita_actualizada,
                'mensaje': 'Cita reprogramada exitosamente'
            }

        except Exception as e:
            return {'success': False, 'error': f'Error al reprogramar: {str(e)}'}

    def cancelar_cita(self, cita_id: int, motivo: str = '') -> Dict[str, Any]:
        """Cancelar una cita"""
        try:
            cita = self.cita_repository.get_cita_by_id(cita_id)
            if not cita:
                return {'success': False, 'error': 'Cita no encontrada'}

            # Validar que se puede cancelar
            if hasattr(cita, 'puede_cancelarse') and not cita.puede_cancelarse:
                return {'success': False, 'error': 'La cita no puede cancelarse (menos de 24 horas)'}

            # Actualizar estado
            cita_cancelada = self.cita_repository.update_cita(cita_id, {
                'estado': 'cancelada',
                'observaciones': f"Cancelada: {motivo}"
            })

            return {
                'success': True,
                'cita': cita_cancelada,
                'mensaje': 'Cita cancelada exitosamente'
            }

        except Exception as e:
            return {'success': False, 'error': f'Error al cancelar: {str(e)}'}

    def obtener_citas_paciente(self, paciente_id: int) -> List:
        """Obtener todas las citas de un paciente"""
        return self.cita_repository.get_citas_by_paciente(paciente_id)

    def obtener_citas_doctor(self, doctor_id: int, fecha: Optional[date] = None) -> List:
        """Obtener citas de un doctor, opcionalmente filtradas por fecha"""
        if fecha:
            return self.cita_repository.get_citas_by_doctor_fecha(doctor_id, fecha)
        return self.cita_repository.get_citas_by_doctor(doctor_id)

    def obtener_ultima_cita(self, paciente_id: int,fecha: str,hora:str) -> Optional:
        """Obtener la última cita de un paciente"""
        citas = self.cita_repository.get_citas_by_paciente(paciente_id)
        if citas and  citas[-1].fecha == datetime.strptime(fecha, '%Y-%m-%d').date() and citas[-1].hora == datetime.strptime(hora, '%H:%M').time():
            return citas[-1]
        return None

    def obtener_citas_urgentes(self) -> List:
        """Obtener todas las citas marcadas como urgentes"""
        return self.cita_repository.get_citas_urgentes()

    def crear_recordatorio_automatico(self, cita) -> Optional:
        """Crear recordatorio automático 24 horas antes de la cita"""
        try:
            fecha_hora_cita = datetime.combine(cita.fecha, cita.hora)
            fecha_recordatorio = fecha_hora_cita - timedelta(hours=24)

            if fecha_recordatorio > datetime.now():
                recordatorio_data = {
                    'paciente': cita.paciente,
                    'cita': cita,
                    'fecha': fecha_recordatorio.date(),
                    'hora': fecha_recordatorio.time(),
                    'mensaje': f'Recordatorio: Tienes una cita mañana a las {cita.hora} con Dr. {cita.doctor.get_full_name()}',
                    'tipo': 'cita_proxima'
                }

                return self.recordatorio_repository.create_recordatorio(recordatorio_data)

        except Exception as e:
            f"Error creando recordatorio: {str(e)}"
            return None

    def obtener_doctores_disponibles(self, fecha_actual, hora_actual):
        """Obtener lista de doctores disponibles para citas urgentes"""
        fecha_actual = datetime.strptime(fecha_actual, '%Y-%m-%d').date() if isinstance(fecha_actual, str) else fecha_actual
        try:
            doctores = self.user_repository.get_all_medicos()
            doctores_disponibles = []
            for doctor in doctores:
                horarios_disponibles = self.obtener_horarios_disponibles(doctor.id, fecha_actual)
                if horarios_disponibles and hora_actual in horarios_disponibles:
                    doctores_disponibles.append(doctor)

            return doctores_disponibles
        except Exception as e:
            f"Error obteniendo doctores disponibles: {str(e)}"
            return []


class RecordatorioService:
    """Servicio para manejar la lógica de negocio de recordatorios"""

    def __init__(self, recordatorio_repository: AbstractRecordatorioRepository = None):
        self.recordatorio_repository = recordatorio_repository or RecordatorioRepository()

    def crear_recordatorio(self, paciente, fecha: str, hora: str,
                           mensaje: str, tipo: str = 'cita_proxima') -> Dict[str, Any]:
        """Crear un recordatorio personalizado"""
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date() if isinstance(fecha, str) else fecha
            hora = datetime.strptime(hora, '%H:%M').time() if isinstance(hora, str) else hora
            recordatorio_data = {
                'paciente': paciente,
                'fecha': fecha,
                'hora': hora,
                'mensaje': mensaje,
                'tipo': tipo
            }

            recordatorio = self.recordatorio_repository.create_recordatorio(recordatorio_data)

            return {
                'success': True,
                'recordatorio': recordatorio,
                'mensaje': 'Recordatorio creado exitosamente'
            }

        except Exception as e:
            return {'success': False, 'error': f'Error al crear recordatorio: {str(e)}'}

    def obtener_recordatorios_paciente(self, paciente_id: int) -> List:
        """Obtener todos los recordatorios de un paciente"""
        return self.recordatorio_repository.get_recordatorios_by_paciente(paciente_id)

    def obtener_recordatorios_pendientes(self) -> List:
        """Obtener recordatorios que no han sido enviados"""
        return self.recordatorio_repository.get_recordatorios_por_enviar()

    def marcar_recordatorio_enviado(self, recordatorio_id: int) -> bool:
        """Marcar un recordatorio como enviado"""
        return self.recordatorio_repository.marcar_recordatorio_enviado(recordatorio_id)

    def procesar_recordatorios_pendientes(self) -> Dict[str, Any]:
        """Procesar todos los recordatorios pendientes de envío"""
        try:
            recordatorios_pendientes = self.obtener_recordatorios_pendientes()
            recordatorios_enviados = 0

            for recordatorio in recordatorios_pendientes:
                # Verificar si es tiempo de enviar el recordatorio
                fecha_hora_recordatorio = datetime.combine(recordatorio.fecha, recordatorio.hora)

                if fecha_hora_recordatorio <= datetime.now():
                    # Aquí iría la lógica de envío (email, SMS, etc.)
                    if self.enviar_recordatorio(recordatorio):
                        self.marcar_recordatorio_enviado(recordatorio.id)
                        recordatorios_enviados += 1

            return {
                'success': True,
                'recordatorios_procesados': len(recordatorios_pendientes),
                'recordatorios_enviados': recordatorios_enviados
            }

        except Exception as e:
            return {'success': False, 'error': f'Error procesando recordatorios: {str(e)}'}

    def enviar_recordatorio(self, recordatorio) -> bool:
        """Simular envío de recordatorio """
        return True


# ======================== INSTANCIAS GLOBALES ========================
cita_service = CitaService()
recordatorio_service = RecordatorioService()