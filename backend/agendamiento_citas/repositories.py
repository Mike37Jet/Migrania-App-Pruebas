# citas/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date, datetime, time
from .models import Cita, Recordatorio, Discapacidad
from usuarios.models import Usuario


# ======================== ABSTRACT REPOSITORIES ========================

class AbstractCitaRepository(ABC):
    """Repositorio abstracto para Citas"""

    @abstractmethod
    def create_cita(self, cita_data: Dict[str, Any]) -> 'Cita':
        pass

    @abstractmethod
    def get_cita_by_id(self, cita_id: int) -> Optional['Cita']:
        pass

    @abstractmethod
    def get_all_citas(self) -> List['Cita']:
        pass

    @abstractmethod
    def get_citas_by_paciente(self, paciente_id: int) -> List['Cita']:
        pass

    @abstractmethod
    def get_citas_by_doctor(self, doctor_id: int) -> List['Cita']:
        pass

    @abstractmethod
    def get_citas_by_fecha(self, fecha: date) -> List['Cita']:
        pass

    @abstractmethod
    def get_citas_by_doctor_fecha(self, doctor_id: int, fecha: date) -> List['Cita']:
        pass

    @abstractmethod
    def update_cita(self, cita_id: int, data: Dict[str, Any]) -> Optional['Cita']:
        pass

    @abstractmethod
    def delete_cita(self, cita_id: int) -> bool:
        pass

    @abstractmethod
    def get_citas_urgentes(self) -> List['Cita']:
        pass


class AbstractRecordatorioRepository(ABC):
    """Repositorio abstracto para Recordatorios"""

    @abstractmethod
    def create_recordatorio(self, recordatorio_data: Dict[str, Any]) -> 'Recordatorio':
        pass

    @abstractmethod
    def get_recordatorio_by_id(self, recordatorio_id: int) -> Optional['Recordatorio']:
        pass

    @abstractmethod
    def get_recordatorios_by_paciente(self, paciente_id: int) -> List['Recordatorio']:
        pass

    @abstractmethod
    def get_all_recordatorios(self) -> List['Recordatorio']:
        pass

    @abstractmethod
    def get_recordatorios_por_enviar(self) -> List['Recordatorio']:
        pass

    @abstractmethod
    def marcar_recordatorio_enviado(self, recordatorio_id: int) -> bool:
        pass


# ======================== DJANGO REPOSITORIES ========================

class CitaRepository(AbstractCitaRepository):
    """Implementación con Django ORM"""

    def create_cita(self, cita_data: Dict[str, Any]) -> Cita:
        return Cita.objects.create(**cita_data)

    def get_cita_by_id(self, cita_id: int) -> Optional[Cita]:
        try:
            return Cita.objects.select_related('doctor', 'paciente').get(id=cita_id)
        except Cita.DoesNotExist:
            return None

    def get_all_citas(self) -> List[Cita]:
        return list(Cita.objects.select_related('doctor', 'paciente').all())

    def get_citas_by_paciente(self, paciente_id: int) -> List[Cita]:
        return list(Cita.objects.filter(paciente_id=paciente_id).select_related('doctor'))

    def get_citas_by_doctor(self, doctor_id: int) -> List[Cita]:
        return list(Cita.objects.filter(doctor_id=doctor_id).select_related('paciente'))

    def get_citas_by_fecha(self, fecha: date) -> List[Cita]:
        return list(Cita.objects.filter(fecha=fecha).select_related('doctor', 'paciente'))

    def get_citas_by_doctor_fecha(self, doctor_id: int, fecha: date) -> List[Cita]:
        return list(Cita.objects.filter(doctor_id=doctor_id, fecha=fecha))

    def update_cita(self, cita_id: int, data: Dict[str, Any]) -> Optional[Cita]:
        try:
            cita = Cita.objects.get(id=cita_id)
            for key, value in data.items():
                setattr(cita, key, value)
            cita.save()
            return cita
        except Cita.DoesNotExist:
            return None

    def delete_cita(self, cita_id: int) -> bool:
        try:
            Cita.objects.get(id=cita_id).delete()
            return True
        except Cita.DoesNotExist:
            return False

    def get_citas_urgentes(self) -> List[Cita]:
        return list(Cita.objects.filter(urgente=True).select_related('doctor', 'paciente'))


class RecordatorioRepository(AbstractRecordatorioRepository):
    """Implementación con Django ORM"""

    def create_recordatorio(self, recordatorio_data: Dict[str, Any]) -> Recordatorio:
        return Recordatorio.objects.create(**recordatorio_data)

    def get_recordatorio_by_id(self, recordatorio_id: int) -> Optional[Recordatorio]:
        try:
            return Recordatorio.objects.select_related('paciente', 'cita').get(id=recordatorio_id)
        except Recordatorio.DoesNotExist:
            return None

    def get_all_recordatorios(self) -> List[Recordatorio]:
        return list(Recordatorio.objects.select_related('paciente', 'cita').all())

    def get_recordatorios_by_paciente(self, paciente_id: int) -> List[Recordatorio]:
        return list(Recordatorio.objects.filter(paciente_id=paciente_id))

    def get_recordatorios_por_enviar(self) -> List[Recordatorio]:
        return list(Recordatorio.objects.filter(enviado=False))

    def marcar_recordatorio_enviado(self, recordatorio_id: int) -> bool:
        try:
            recordatorio = Recordatorio.objects.get(id=recordatorio_id)
            recordatorio.marcar_como_enviado()
            return True
        except Recordatorio.DoesNotExist:
            return False


# ======================== FAKE REPOSITORIES (PARA TESTING) ========================

class FakeCita:
    """Clase que simula el modelo Cita para testing"""
    _id_counter = 1

    def __init__(self, doctor, paciente, fecha, hora, urgente=False, estado='pendiente', **kwargs):
        self.id = FakeCita._id_counter
        FakeCita._id_counter += 1
        self.doctor = doctor
        self.paciente = paciente
        self.fecha = fecha if isinstance(fecha, date) else datetime.strptime(fecha, '%Y-%m-%d').date()
        self.hora = hora if isinstance(hora, time) else datetime.strptime(hora, '%H:%M').time()
        self.urgente = urgente
        self.estado = estado
        self.motivo = kwargs.get('motivo', '')
        self.observaciones = kwargs.get('observaciones', '')
        self.creada_en = datetime.now()
        self.actualizada_en = datetime.now()

    @property
    def fecha_hora_completa(self):
        return datetime.combine(self.fecha, self.hora)

    def __eq__(self, other):
        if not isinstance(other, FakeCita):
            return False
        return (self.doctor == other.doctor and
                self.paciente == other.paciente and
                self.fecha == other.fecha and
                self.hora == other.hora)
    def __repr__(self):
        return f"FakeCita(id={self.id}, doctor={self.doctor}, paciente={self.paciente}, fecha={self.fecha}, hora={self.hora}, estado={self.estado})"


class FakeRecordatorio:
    """Clase que simula el modelo Recordatorio para testing"""
    _id_counter = 1

    def __init__(self, paciente, fecha, hora, mensaje='', tipo='cita_proxima', **kwargs):
        self.id = FakeRecordatorio._id_counter
        FakeRecordatorio._id_counter += 1
        self.paciente = paciente
        self.fecha = fecha if isinstance(fecha, date) else datetime.strptime(fecha, '%Y-%m-%d').date()
        self.hora = hora if isinstance(hora, time) else datetime.strptime(hora, '%H:%M').time()
        self.mensaje = mensaje
        self.tipo = tipo
        self.enviado = False
        self.creado_en = datetime.now()
        self.enviado_en = None
        self.cita = kwargs.get('cita')

    def marcar_como_enviado(self):
        self.enviado = True
        self.enviado_en = datetime.now()
    def __eq__(self, other):
        if not isinstance(other, FakeRecordatorio):
            return False
        return (self.paciente == other.paciente and
                self.fecha == other.fecha and
                self.hora == other.hora)
    def __repr__(self):
        return f"FakeRecordatorio(id={self.id}, paciente={self.paciente}, fecha={self.fecha}, hora={self.hora})"




class FakeCitaRepository(AbstractCitaRepository):
    """Implementación fake para testing"""

    def __init__(self):
        self.citas: List[FakeCita] = []

    def create_cita(self, cita_data: Dict[str, Any]) -> FakeCita:
        cita = FakeCita(**cita_data)
        self.citas.append(cita)
        return cita


    def get_cita_by_id(self, cita_id: int) -> Optional[FakeCita]:
        return next((c for c in self.citas if c.id == cita_id), None)

    def get_citas_by_paciente(self, paciente_id: int) -> List[FakeCita]:
        return [c for c in self.citas if c.paciente.id == paciente_id]

    def get_all_citas(self) -> list[FakeCita]:
        return self.citas

    def get_citas_by_doctor(self, doctor_id: int) -> List[FakeCita]:
        return [c for c in self.citas if c.doctor.id == doctor_id]

    def get_citas_by_fecha(self, fecha: date) -> List[FakeCita]:
        return [c for c in self.citas if c.fecha == fecha]

    def get_citas_by_doctor_fecha(self, doctor_id: int, fecha: date) -> List[FakeCita]:
        return [c for c in self.citas if c.doctor.id == doctor_id and c.fecha == fecha]

    def update_cita(self, cita_id: int, data: Dict[str, Any]) -> Optional[FakeCita]:
        cita = self.get_cita_by_id(cita_id)
        if cita:
            for key, value in data.items():
                setattr(cita, key, value)
        return cita

    def delete_cita(self, cita_id: int) -> bool:
        cita = self.get_cita_by_id(cita_id)
        if cita:
            self.citas.remove(cita)
            return True
        return False

    def get_citas_urgentes(self) -> List[FakeCita]:
        return [c for c in self.citas if c.urgente]


class FakeRecordatorioRepository(AbstractRecordatorioRepository):
    """Implementación fake para testing"""

    def __init__(self):
        self.recordatorios: List[FakeRecordatorio] = []

    def create_recordatorio(self, recordatorio_data: Dict[str, Any]) -> FakeRecordatorio:
        recordatorio = FakeRecordatorio(**recordatorio_data)
        self.recordatorios.append(recordatorio)
        return recordatorio

    def get_recordatorio_by_id(self, recordatorio_id: int) -> Optional[FakeRecordatorio]:
        return next((r for r in self.recordatorios if r.id == recordatorio_id), None)

    def get_all_recordatorios(self) -> list[FakeRecordatorio]:
        return self.recordatorios


    def get_recordatorios_by_paciente(self, paciente_id: int) -> List[FakeRecordatorio]:
        return [r for r in self.recordatorios if r.paciente.id == paciente_id]

    def get_recordatorios_por_enviar(self) -> List[FakeRecordatorio]:
        return [r for r in self.recordatorios if not r.enviado]

    def marcar_recordatorio_enviado(self, recordatorio_id: int) -> bool:
        recordatorio = self.get_recordatorio_by_id(recordatorio_id)
        if recordatorio:
            recordatorio.marcar_como_enviado()
            return True
        return False