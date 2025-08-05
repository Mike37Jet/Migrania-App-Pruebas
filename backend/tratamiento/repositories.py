from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from django.utils import timezone
from tratamiento.models import Medicamento, Tratamiento, Recordatorio, Alerta, EstadoNotificacion

class BaseRepository(ABC):
    @abstractmethod
    def get_medicamento_by_id(self, id):
        pass

    @abstractmethod
    def get_all_medicamentos(self):
        pass

    @abstractmethod
    def save_medicamento(self, medicamento):
        pass

    @abstractmethod
    def get_tratamiento_by_id(self, id):
        pass

    @abstractmethod
    def get_all_tratamientos(self):
        pass

    @abstractmethod
    def save_tratamiento(self, tratamiento):
        pass

    @abstractmethod
    def add_medicamento_to_tratamiento(self, tratamiento_id, medicamento_id):
        pass

    @abstractmethod
    def get_recordatorios_by_tratamiento(self, tratamiento_id):
        pass

    @abstractmethod
    def get_recordatorio_by_id(self, id):
        pass

    @abstractmethod
    def save_recordatorio(self, recordatorio):
        pass

    @abstractmethod
    def get_alerta_by_id(self, id):
        pass

    @abstractmethod
    def get_alertas_by_tratamiento(self, tratamiento_id):
        pass

    @abstractmethod
    def save_alerta(self, alerta):
        pass

    @abstractmethod
    def get_notificaciones_pendientes(self, tratamiento_id, fecha_hora=None):
        pass

    @abstractmethod
    def get_siguiente_alerta(self, tratamiento_id, ahora=None):
        pass


class DjangoRepository(BaseRepository):
    def get_medicamento_by_id(self, id):
        try:
            return Medicamento.objects.get(pk=id)
        except Medicamento.DoesNotExist:
            return None

    def get_all_medicamentos(self):
        return Medicamento.objects.all()

    def save_medicamento(self, medicamento):
        medicamento.save()
        return medicamento

    def get_tratamiento_by_id(self, id):
        try:
            return Tratamiento.objects.get(pk=id)
        except Tratamiento.DoesNotExist:
            return None

    def get_all_tratamientos(self):
        return Tratamiento.objects.all()

    def save_tratamiento(self, tratamiento):
        tratamiento.save()
        return tratamiento

    def add_medicamento_to_tratamiento(self, tratamiento_id, medicamento_id):
        tratamiento = self.get_tratamiento_by_id(tratamiento_id)
        medicamento = self.get_medicamento_by_id(medicamento_id)
        if tratamiento and medicamento:
            tratamiento.medicamentos.add(medicamento)
            return True
        return False

    def get_recordatorios_by_tratamiento(self, tratamiento_id):
        tratamiento = self.get_tratamiento_by_id(tratamiento_id)
        if tratamiento:
            return tratamiento.recordatorios.all()
        return []

    def get_recordatorio_by_id(self, id):
        try:
            return Recordatorio.objects.get(pk=id)
        except Recordatorio.DoesNotExist:
            return None

    def save_recordatorio(self, recordatorio):
        recordatorio.save()
        return recordatorio

    def get_alerta_by_id(self, id):
        try:
            return Alerta.objects.get(pk=id)
        except Alerta.DoesNotExist:
            return None

    def get_alertas_by_tratamiento(self, tratamiento_id):
        tratamiento = self.get_tratamiento_by_id(tratamiento_id)
        if tratamiento:
            return tratamiento.alertas.all()
        return []

    def save_alerta(self, alerta):
        alerta.save()
        return alerta

    def get_notificaciones_pendientes(self, tratamiento_id, fecha_hora=None):
        if fecha_hora is None:
            fecha_hora = timezone.now()

        tratamiento = self.get_tratamiento_by_id(tratamiento_id)
        if tratamiento:
            alertas = list(tratamiento.alertas.filter(
                estado=EstadoNotificacion.ACTIVO,
                fecha_hora__lte=fecha_hora
            ))

            recordatorios = list(tratamiento.recordatorios.filter(
                estado=EstadoNotificacion.ACTIVO,
                fecha_hora__lte=fecha_hora
            ))

            return sorted(alertas + recordatorios, key=lambda x: x.fecha_hora)
        return []

    def get_siguiente_alerta(self, tratamiento_id, ahora=None):
        if ahora is None:
            ahora = timezone.now()

        tratamiento = self.get_tratamiento_by_id(tratamiento_id)
        if tratamiento:
            return tratamiento.alertas.filter(
                estado=EstadoNotificacion.ACTIVO,
                fecha_hora__gte=ahora
            ).order_by('fecha_hora').first()
        return None


class FakeRepository(BaseRepository):
    def __init__(self):
        self.medicamentos = {}
        self.tratamientos = {}
        self.recordatorios = {}
        self.alertas = {}
        self.tratamiento_medicamentos = {}
        self.next_id = {
            'medicamento': 1,
            'tratamiento': 1,
            'recordatorio': 1,
            'alerta': 1
        }

    def _get_next_id(self, tipo):
        id = self.next_id[tipo]
        self.next_id[tipo] += 1
        return id

    def get_medicamento_by_id(self, id):
        return self.medicamentos.get(id)

    def get_all_medicamentos(self):
        return list(self.medicamentos.values())

    def save_medicamento(self, medicamento):
        if not medicamento.id:
            medicamento.id = self._get_next_id('medicamento')
        self.medicamentos[medicamento.id] = medicamento
        return medicamento

    def get_tratamiento_by_id(self, id):
        return self.tratamientos.get(id)

    def get_all_tratamientos(self):
        return list(self.tratamientos.values())

    def save_tratamiento(self, tratamiento):
        if not tratamiento.id:
            tratamiento.id = self._get_next_id('tratamiento')
            self.tratamiento_medicamentos[tratamiento.id] = set()
        self.tratamientos[tratamiento.id] = tratamiento
        return tratamiento

    def add_medicamento_to_tratamiento(self, tratamiento_id, medicamento_id):
        if tratamiento_id in self.tratamientos and medicamento_id in self.medicamentos:
            if tratamiento_id not in self.tratamiento_medicamentos:
                self.tratamiento_medicamentos[tratamiento_id] = set()
            self.tratamiento_medicamentos[tratamiento_id].add(medicamento_id)
            return True
        return False

    def get_recordatorios_by_tratamiento(self, tratamiento_id):
        return [r for r in self.recordatorios.values() if getattr(r, 'tratamiento_id', None) == tratamiento_id]

    def get_recordatorio_by_id(self, id):
        return self.recordatorios.get(id)

    def save_recordatorio(self, recordatorio):
        if not recordatorio.id:
            recordatorio.id = self._get_next_id('recordatorio')
        self.recordatorios[recordatorio.id] = recordatorio
        return recordatorio

    def get_alerta_by_id(self, id):
        return self.alertas.get(id)

    def get_alertas_by_tratamiento(self, tratamiento_id):
        return [a for a in self.alertas.values() if getattr(a, 'tratamiento_id', None) == tratamiento_id]

    def save_alerta(self, alerta):
        if not alerta.id:
            alerta.id = self._get_next_id('alerta')
        self.alertas[alerta.id] = alerta
        return alerta

    def get_notificaciones_pendientes(self, tratamiento_id, fecha_hora=None):
        if fecha_hora is None:
            fecha_hora = timezone.now()

        alertas = [
            a for a in self.alertas.values()
            if getattr(a, 'tratamiento_id', None) == tratamiento_id
            and a.estado == EstadoNotificacion.ACTIVO
            and a.fecha_hora <= fecha_hora
        ]

        recordatorios = [
            r for r in self.recordatorios.values()
            if getattr(r, 'tratamiento_id', None) == tratamiento_id
            and r.estado == EstadoNotificacion.ACTIVO
            and r.fecha_hora <= fecha_hora
        ]

        return sorted(alertas + recordatorios, key=lambda x: x.fecha_hora)

    def get_medicamentos_by_tratamiento_id(self, tratamiento_id):
        ids = self.tratamiento_medicamentos.get(tratamiento_id, set())
        return [self.medicamentos[mid] for mid in ids if mid in self.medicamentos]


    def get_siguiente_alerta(self, tratamiento_id, ahora=None):
        pass
