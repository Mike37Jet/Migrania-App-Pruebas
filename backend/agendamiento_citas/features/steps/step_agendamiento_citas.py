from behave import *
import django
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# Configurar Django al inicio del archivo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Ajusta según tu proyecto
django.setup()

# Imports según tu estructura real
from agendamiento_citas.repositories import FakeCitaRepository, FakeRecordatorioRepository
from agendamiento_citas.services import CitaService, RecordatorioService
from usuarios.repositories import FakeUserRepository

use_step_matcher("re")
# Inicializar repositorios fake para testing
fake_user_repo = FakeUserRepository()
fake_cita_repo = FakeCitaRepository()
fake_recordatorio_repo = FakeRecordatorioRepository()

# Inicializar servicios con repositorios fake
cita_service_fake = CitaService(
    cita_repository=fake_cita_repo,
    recordatorio_repository=fake_recordatorio_repo,
    user_repository=fake_user_repo
)
recordatorio_service_fake = RecordatorioService(recordatorio_repository=fake_recordatorio_repo)

@step("que hay disponibilidad con el (?P<doctor>.+) con (?P<cedula>.+) el (?P<fecha_cita>.+) a las (?P<hora_cita>.+)")
def step_impl(context, doctor, cedula,fecha_cita, hora_cita):
    context.doctor = fake_user_repo.get_user_by_cedula(cedula)
    context.fecha_cita = fecha_cita
    context.hora_cita = hora_cita
    assert context.doctor is not None, f"Doctor con cédula {cedula} no encontrado"
    assert cita_service_fake.esta_disponibilidad_doctor(context.doctor.id,context.fecha_cita,context.hora_cita), \
        "El doctor no está disponible en la fecha y hora especificadas"

@step("(?P<nombre_paciente>.+) con (?P<cedula_paciente>.+) agenda una cita")
def step_impl(context,nombre_paciente, cedula_paciente):
    context.paciente = fake_user_repo.get_user_by_cedula(cedula_paciente)
    assert context.paciente is not None, f"Paciente con cédula {cedula_paciente} no encontrado"
    cita_agendada = cita_service_fake.crear_cita(context.doctor.id, context.paciente.id, context.fecha_cita, context.hora_cita)
    assert cita_agendada['success'] , "La cita no fue creada correctamente"

@step("el paciente recibe un recordatorio para el (?P<fecha_recordatorio>.+) a las (?P<hora_recordatorio>.+)")
def step_impl(context, fecha_recordatorio, hora_recordatorio):
    context.fecha_recordatorio = fecha_recordatorio
    context.hora_recordatorio = hora_recordatorio
    recordatorio = recordatorio_service_fake.crear_recordatorio(context.paciente,context.fecha_recordatorio, context.hora_recordatorio,"Recordatorio de cita médica")
    assert recordatorio['success'], "El recordatorio no fue creado correctamente"


@step(r'que el paciente con cedula "(?P<cedula_paciente>\d{10})" presenta discapacidad severa')
def step_impl(context,cedula_paciente):
    context.paciente = fake_user_repo.get_user_by_cedula(cedula_paciente)
    assert context.paciente is not None, f"Paciente con cédula {cedula_paciente} no encontrado"
    #assert context.paciente.get_discapacidad == Discapacidad.SEVERA, "El paciente no fue marcado con discapacidad severa"

@step("el paciente agenda una atención medica urgente")
def step_impl(context):
    context.cita_urgente_agendada = cita_service_fake.crear_cita_urgente(context.paciente.id)
    assert context.cita_urgente_agendada['success'], "La cita urgente no fue creada correctamente"


@step("se asigna un doctor disponible inmediatamente")
def step_impl(context):
    assert context.cita_urgente_agendada['cita'].doctor is not None, "No se asigno un doctor disponible para la cita urgente"

@step(
    "que (?P<nombre_paciente>.+) con (?P<cedula_paciente>.+) tiene una cita agendada con el doctor (?P<doctor>.+) con (?P<cedula_doctor>.+) el (?P<fecha_original>.+) a las (?P<hora_original>.+)")
def step_impl(context, nombre_paciente, cedula_paciente, doctor, cedula_doctor, fecha_original, hora_original):
    context.paciente = fake_user_repo.get_user_by_cedula(cedula_paciente)
    context.doctor_original = fake_user_repo.get_user_by_cedula(cedula_doctor)
    context.fecha_original = fecha_original
    context.hora_original = hora_original
    context.ultima_cita = cita_service_fake.obtener_ultima_cita(context.paciente.id,fecha_original,hora_original)
    assert context.ultima_cita is not None, "No se encontró una cita agendada para el paciente en esa fecha y hora"

@step("solicita una reprogramación para (?P<fecha_nueva>.+) con al menos 24 horas de anticipación")
def step_impl(context,fecha_nueva):
    context.fecha_nueva = fecha_nueva
    fecha_hora_cita = datetime.strptime(f"{context.fecha_original} {context.hora_original}", "%Y-%m-%d %H:%M")
    ahora = datetime.now()
    diferencia = fecha_hora_cita - ahora
    assert diferencia >= timedelta(hours=24), "La reprogramación no se solicitó con al menos 24 horas de anticipación"

@step("se sugiere automáticamente un horario alternativo disponible")
def step_impl(context):
    horarios_disponibles = cita_service_fake.obtener_horarios_disponibles(context.doctor_original.id, context.fecha_nueva)
    assert horarios_disponibles , "No hay horarios disponibles para el doctor sugerido"
    context.horarios_disponibles = horarios_disponibles

@step("se reorganiza la cita")
def step_impl(context):
   cita_reprogramada = cita_service_fake.reprogramar_cita(context.ultima_cita.id, context.fecha_nueva, context.horarios_disponibles[0])
   assert cita_reprogramada['success'], "La cita no se reprogramó correctamente"
