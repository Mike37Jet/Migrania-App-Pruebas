import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migraine_app.settings')
django.setup()
from usuarios.models import PacienteProfile
from behave import step, use_step_matcher
from datetime import datetime, timedelta
from tratamiento.models import Recordatorio, Alerta, EstadoNotificacion, Recomendacion
from tratamiento.repositories import FakeRepository
from faker import Faker
from tratamiento.services import TratamientoService
import logging
import warnings

fake = Faker('es_ES')
warnings.filterwarnings("ignore", category=RuntimeWarning, message="DateTimeField .* received a naive datetime")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
use_step_matcher("re")

@step("que el paciente tiene una medicina prescrita para la migraña")
def step_impl(context):
    context.repository = FakeRepository()
    context.service = TratamientoService(context.repository)

    hora_actual = datetime.now().time()
    from django.contrib.auth import get_user_model
    User = get_user_model()

    context.usuario_paciente = User.objects.create_user(
        username=fake.user_name(),
        email=fake.unique.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        cedula=str(fake.unique.random_number(digits=10, fix_len=True)),
        tipo_usuario='paciente',
        genero=fake.random_element(['M', 'F', 'O', 'N']),
    )

    context.paciente = PacienteProfile.objects.create(
        usuario=context.usuario_paciente,
        contacto_emergencia_nombre=fake.name(),
        contacto_emergencia_telefono=fake.phone_number()[:15],
        contacto_emergencia_relacion="Padre"
    )

    context.medicamento = context.service.crear_medicamento(
        nombre="Ibuprofeno",
        dosis="400mg",
        caracteristica="Anti-inflamatorio",
        hora_inicio=hora_actual,
        frecuencia_horas=8,
        duracion_dias=5
    )

    context.tratamiento = context.service.crear_tratamiento(
        fecha_inicio=datetime.now().date(),
        paciente=context.paciente,
        activo=True
    )

    medicamento_id = context.medicamento.id
    tratamiento_id = context.tratamiento.id
    context.repository.add_medicamento_to_tratamiento(tratamiento_id, medicamento_id)

    assert context.medicamento is not None, "No se pudo crear el medicamento"
    assert context.tratamiento is not None, "No se pudo crear el tratamiento"

@step("la hora actual sea 30 minutos antes de la hora de la toma")
def step_impl(context):
    context.hora_toma = datetime.combine(
        datetime.now().date(),
        context.medicamento.hora_de_inicio
    )

    context.hora_actual = context.hora_toma - timedelta(minutes=30)

    context.notificaciones = context.service.generar_notificaciones(
        context.tratamiento.id,
        context.hora_actual.date()
    )

@step("se enviará un recordatorio al paciente indicando que debe tomar su medicación pronto")
def step_impl(context):
    recordatorios = [n for n in context.notificaciones if isinstance(n, Recordatorio)]

@step('el estado del recordatorio será "activo"')
def step_impl(context):
    recordatorios = [n for n in context.notificaciones if isinstance(n, Recordatorio)]
    for recordatorio in recordatorios:
        if "Recordatorio para tomar" in recordatorio.mensaje:
            assert recordatorio.estado == EstadoNotificacion.ACTIVO, \
                f"El estado del recordatorio es {recordatorio.estado}, debería ser {EstadoNotificacion.ACTIVO}"

@step("que el paciente ha recibido una (?P<numero_alerta>.*) alerta para tomar su medicación")
def step_impl(context, numero_alerta):
    numero_map = {"primera": 1, "segunda": 2, "tercera": 3}
    num_alerta = numero_map.get(numero_alerta.lower(), 1)

    context.alerta = Alerta(
        mensaje=f"Es hora de tomar Ibuprofeno (Alerta #{num_alerta})",
        fecha_hora=datetime.now(),
        estado=EstadoNotificacion.ACTIVO,
        tratamiento=context.repository.get_tratamiento_by_id(context.tratamiento.id),
        numero_alerta=num_alerta,
        duracion=15,
        tiempo_espera=15
    )
    context.repository.save_alerta(context.alerta)
    context.num_alerta = num_alerta
    context.alerta.enviar()

@step("la hora actual es (?P<tiempo_transcurrido>\\d+) minutos después de la hora programada para la toma")
def step_impl(context, tiempo_transcurrido):
    tiempo_transcurrido = int(tiempo_transcurrido)
    context.hora_programada = context.alerta.fecha_hora
    context.hora_actual = context.hora_programada + timedelta(minutes=tiempo_transcurrido)

@step("transcurran 15 minutos sin que el paciente confirme la toma")
def step_impl(context):
    context.hora_transcurrida = context.hora_actual + timedelta(minutes=15)
    context.nueva_alerta = context.alerta.reenviar(context.hora_transcurrida)
    if context.nueva_alerta:
        context.repository.save_alerta(context.nueva_alerta)

@step('se actualizará el estado de la alerta a "sin confirmar"')
def step_impl(context):
    alerta_actualizada = context.repository.get_alerta_by_id(context.alerta.id)
    assert alerta_actualizada.estado == EstadoNotificacion.CONFIRMADO_NO_TOMADO, \
        f"El estado de la alerta es {alerta_actualizada.estado}, debería ser {EstadoNotificacion.CONFIRMADO_NO_TOMADO}"

@step("se programará una (?P<accion_siguiente>.*) alerta")
def step_impl(context, accion_siguiente):
    if accion_siguiente.lower() == "ninguna":
        assert context.nueva_alerta is None, "Se programó una alerta cuando no debería haberse programado ninguna"
    else:
        assert context.nueva_alerta is not None, "No se programó una nueva alerta cuando debería haberse programado"
        siguiente_num = context.num_alerta + 1
        assert context.nueva_alerta.numero_alerta == siguiente_num, \
            f"El número de la nueva alerta es {context.nueva_alerta.numero_alerta}, debería ser {siguiente_num}"

@step("el paciente confirma que (?P<estado_toma>.*) ha tomado la medicación")
def step_impl(context, estado_toma):
    tomado = estado_toma.lower() == "si"
    if tomado:
        context.estado_resultado = context.alerta.confirmarTomado(context.hora_actual)
    else:
        context.estado_resultado = context.alerta.confirmarNoTomado()
    context.repository.save_alerta(context.alerta)

@step('se actualizará el estado de la alerta a "(?P<estado_resultado>.*)"')
def step_impl(context, estado_resultado):
    estado_map = {
        "tomado": EstadoNotificacion.CONFIRMADO_TOMADO,
        "tomado tarde": EstadoNotificacion.CONFIRMADO_TOMADO_TARDE,
        "tomado muy tarde": EstadoNotificacion.CONFIRMADO_TOMADO_MUY_TARDE,
        "no tomado": EstadoNotificacion.CONFIRMADO_NO_TOMADO,
    }
    estado_esperado = estado_map.get(estado_resultado, None)
    assert estado_esperado is not None, f"Estado no reconocido: {estado_resultado}"

    alerta_actualizada = context.repository.get_alerta_by_id(context.alerta.id)
    assert alerta_actualizada.estado == estado_esperado, \
        f"El estado de la alerta es {alerta_actualizada.estado}, debería ser {estado_esperado}"

@step("que el paciente tiene una recomendación de tratamiento para la migraña")
def step_impl(context):
    context.tratamiento = context.service.crear_tratamiento(
        paciente=context.paciente,
        recomendaciones=[Recomendacion.HIDRATACION],
        fecha_inicio=datetime.now().date(),
        activo=True
    )

    assert len(context.tratamiento.recomendaciones) > 0, "No se agregaron recomendaciones al tratamiento"
    assert Recomendacion.HIDRATACION in context.tratamiento.recomendaciones, "No se encontró la recomendación de hidratación"

@step("sea las 9 horas del día")
def step_impl(context):
    today = datetime.now().date()
    context.hora_actual = datetime.combine(today, datetime.min.time().replace(hour=9))

    context.notificaciones = context.service.generar_notificaciones(
        context.tratamiento.id,
        context.hora_actual.date()
    )

    assert len(context.notificaciones) > 0, f"No se generaron notificaciones en absoluto para el tratamiento {context.tratamiento.id}"

@step("se notificará mediante un recordatorio sugiriéndole seguir esta recomendación")
def step_impl(context):
    recordatorios = [n for n in context.notificaciones if isinstance(n, Recordatorio)]

    assert len(recordatorios) > 0, "No se generaron recordatorios para las recomendaciones"

    recordatorio_recomendacion = False
    for recordatorio in recordatorios:
        if "Recordatorio de recomendación" in recordatorio.mensaje:
            recordatorio_recomendacion = True
            break

    assert recordatorio_recomendacion, "No se encontró un recordatorio con mensaje de recomendación"

@step('el estado de la recordatorio será "activo"')
def step_impl(context):
    recordatorios = [n for n in context.notificaciones if isinstance(n, Recordatorio)]
    for recordatorio in recordatorios:
        if "Recordatorio de recomendación" in recordatorio.mensaje:
            assert recordatorio.estado == EstadoNotificacion.ACTIVO, \
                f"El estado del recordatorio es {recordatorio.estado}, debería ser {EstadoNotificacion.ACTIVO}"
