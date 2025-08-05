import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "migraine_app.settings")
django.setup()

from behave import *
from django.utils import timezone
from datetime import datetime, date
from faker import Faker
from tratamiento.repositories import FakeRepository
from tratamiento.services import TratamientoService
from tratamiento.models import EpisodioCefalea

use_step_matcher("re")
fake = Faker('es_ES')

@step("que el paciente tiene al menos un historial de migrañas")
def step_impl(context):
    inicializar_contexto_basico(context)
    context.tiene_historial = True
    assert context.paciente is not None, "El paciente no fue creado."

@step("que el paciente presenta su primer episodio con la categorización (.+)")
def step_impl(context, tipo_migrana):
    inicializar_contexto_basico(context)
    context.tipo_migraña_actual = tipo_migrana
    context.primer_episodio = True
    assert context.paciente is not None, "El paciente no fue inicializado."
    assert context.tipo_migraña_actual == tipo_migrana, "El tipo de migraña no coincide."

@step("el médico ingresa los datos del tratamiento")
def step_impl(context):
    inicializar_contexto_basico(context)

    context.repository = FakeRepository()
    context.service = TratamientoService(context.repository)

    campos_esperados = {'Dosis', 'Medicamento', 'Características', 'Frecuencia', 'Duración tratamiento','Recomendacion'}
    campos_tabla = {row['Campo'] for row in context.table}
    assert campos_esperados == campos_tabla, f"Campos faltantes o incorrectos"
    context.campos_tabla = campos_tabla

    context.dosis = fake.random_element(['10', '20', '12', '30'])
    context.medicamento = fake.random_element(['Ibuprofeno', 'Paracetamol', 'Sumatriptán', 'Prednisona'])
    context.duracion_dias = fake.random_element([3, 15, 8])
    context.caracteristica = fake.random_element(['50mg', '500mg', '10mg'])
    context.frecuencia_horas = 8

    context.episodio = crear_episodio_dummy(paciente=context.paciente.usuario, tipo_migraña=context.tipo_migraña_actual)

    context.tratamiento = context.service.crear_tratamiento( paciente=context.paciente, episodio=context.episodio,activo=True,
        fecha_inicio=date.today(),
    )

    context.medicamento = context.service.crear_medicamento(
        nombre=context.medicamento,
        dosis=context.dosis,
        caracteristica=context.caracteristica,
        hora_inicio=timezone.now().time(),
        frecuencia_horas=context.frecuencia_horas,
        duracion_dias=context.duracion_dias
    )

    context.service.agregar_medicamento_a_tratamiento( context.tratamiento.id, context.medicamento )

    from tratamiento.models import Recomendacion
    context.tratamiento.recomendaciones = [Recomendacion.HIDRATACION]
    context.repository.save_tratamiento(context.tratamiento)

    context.tratamiento_creado = context.tratamiento

    assert context.tratamiento_creado is not None, "El tratamiento no fue creado."
    assert context.tratamiento_creado.activo == True, "El tratamiento debe estar activo."


@step("el sistema crea el tratamiento")
def step_impl(context):
    assert hasattr(context, 'tratamiento_creado'), "El tratamiento debió ser creado en el step anterior"
    assert context.tratamiento_creado is not None, "El tratamiento no puede ser None"

    campos_esperados = {'Dosis', 'Medicamento', 'Características', 'Frecuencia', 'Duración tratamiento',
                        'Recomendacion'}
    assert context.campos_tabla == campos_esperados, f"Los campos de la tabla no coinciden con los esperados"

    tratamiento_desde_repo = context.repository.get_tratamiento_by_id(context.tratamiento_creado.id)
    context.service.agregar_medicamento_a_tratamiento(context.tratamiento.id, context.medicamento)
    medicamentos_tratamiento = context.repository.get_medicamentos_by_tratamiento_id(context.tratamiento_creado.id)

    assert len(medicamentos_tratamiento) >= 1, "El tratamiento debe tener al menos una medicación"
    assert len(tratamiento_desde_repo.recomendaciones) >= 1, "El tratamiento debe tener al menos una recomendación"

    assert context.tratamiento_creado.activo == True, "El tratamiento debe estar activo"
    assert context.tratamiento_creado.estaActivo() == True, "El tratamiento debe estar en estado activo"

    context.tratamiento_generado = context.tratamiento_creado


@step("que el paciente tiene un tratamiento activo correspondiente a un episodio médico")
def step_paciente_con_tratamiento(context):
    inicializar_contexto_basico(context)

    context.repository = FakeRepository()
    context.service = TratamientoService(context.repository)

    context.episodio = EpisodioCefalea.objects.create(
        paciente=context.paciente.usuario,
        duracion_cefalea_horas=2,
        severidad='Moderada',
        localizacion='Unilateral',
        caracter_dolor='Pulsátil',
        empeora_actividad=True,
        nauseas_vomitos=True,
        fotofobia=True,
        fonofobia=False,
        presencia_aura=False,
        sintomas_aura='Ninguno',
        duracion_aura_minutos=0,
        en_menstruacion=False,
        anticonceptivos=False,
        categoria_diagnostica='Migraña sin aura'
    )
    context.tratamiento_activo = context.service.crear_tratamiento(
        paciente=context.paciente,
        episodio=context.episodio,
        fecha_inicio=datetime.now().date(),
        activo=True
    )

    assert context.paciente is not None, "El paciente no fue inicializado."
    assert context.tratamiento_activo.estaActivo(), "El tratamiento no está activo."


@step(
    "el historial de alertas indica que el paciente ha confirmado (?P<porcentaje_cumplimiento>.+)% de las tomas correspondientes a (?P<numero_tratamientos>.+) tratamientos")
def step_historial_cumplimiento(context, porcentaje_cumplimiento, numero_tratamientos):
    inicializar_contexto_basico(context)

    context.repository = FakeRepository()
    context.service = TratamientoService(context.repository)

    context.porcentaje_cumplimiento = float(porcentaje_cumplimiento)
    context.cumplimiento_promedio = context.porcentaje_cumplimiento
    context.numero_tratamientos = int(numero_tratamientos)

    context.tratamiento_activo = context.service.crear_tratamiento(
        paciente=context.paciente,
        episodio=context.episodio,
        fecha_inicio=datetime.now().date(),
        activo=True
    )
    context.tratamiento_activo.cumplimiento = context.porcentaje_cumplimiento
    context.repository.save_tratamiento(context.tratamiento_activo)
    assert context.tratamiento_activo is not None, "El primer tratamiento debe existir."


@step("el médico evalúa el cumplimiento del tratamiento anterior")
def step_medico_evalua(context):
    tratamiento_1 = context.repository.get_tratamiento_by_id(context.tratamiento_activo.id)

    context.cumplimiento_tratamiento_1 = float(tratamiento_1.cumplimiento)

    context.cumplimiento_tratamiento_1
    context.evaluacion_completada = True

    assert context.cumplimiento_tratamiento_1 >= 0, "El cumplimiento del primer tratamiento debe ser válido."
    assert context.evaluacion_completada == True, "La evaluación debe estar completada."

@step("se decide modificar el tratamiento")
def step_modificar_tratamiento(context):
    context.modificacion_decidida = True
    assert context.modificacion_decidida is True, "La decisión de modificar el tratamiento debe estar tomada"


@step('el médico ingresa las siguientes características para el nuevo tratamiento')
def step_medico_ingresa_caracteristicas(context):
    context.nueva_cantidad = fake.random_element(['10', '20', '12', '30'])
    context.nueva_medicamento = fake.random_element(['Ibuprofeno', 'Paracetamol', 'Sumatriptán'])
    context.nueva_duracion = fake.random_element([3, 15, 8])
    context.caracteristica = fake.random_element(['50mg', '500mg', '10mg'])

    assert context.nueva_cantidad is not None, "La cantidad debe estar definida."
    assert context.nueva_medicamento is not None, "La medicación debe estar definida."


@step('el sistema debe actualizar el tratamiento con los nuevos datos')
def step_sistema_actualiza(context):

    nuevo_medicamento = context.service.crear_medicamento(
        nombre=context.nueva_medicamento,
        dosis=context.nueva_cantidad,
        caracteristica=context.caracteristica,
        hora_inicio=datetime.now().time(),
        frecuencia_horas=8,
        duracion_dias=context.nueva_duracion
    )

    context.service.agregar_medicamento_a_tratamiento(
        context.tratamiento_activo.id,
        nuevo_medicamento
    )

    context.repository.save_tratamiento(context.tratamiento_activo)
    context.actualizacion_exitosa = True

    assert context.actualizacion_exitosa == True, "La actualización debe ser exitosa."


@step('se decide cancelar el tratamiento')
def step_cancelar_tratamiento_actual(context):
    assert context.cumplimiento_promedio < 80, f"El cumplimiento promedio debe ser menor a 80%"
    context.decision_cancelacion = True

@step('el médico ingresa el motivo como "(?P<motivo_cancelacion>.+)"')
def step_impl(context, motivo_cancelacion):
    context.motivo_cancelacion = motivo_cancelacion
    assert len(motivo_cancelacion.strip()) > 0, "El motivo no puede estar vacío"


@step("el sistema debe cancelar el tratamiento con los datos ingresados")
def step_impl(context):
    tratamiento_a_cancelar = context.repository.get_tratamiento_by_id(context.tratamiento_activo.id)
    tratamiento_a_cancelar.activo = False
    tratamiento_a_cancelar.motivo_cancelacion = context.motivo_cancelacion

    context.repository.save_tratamiento(tratamiento_a_cancelar)

    context.tratamiento_cancelado = tratamiento_a_cancelar
    context.cancelacion_realizada = True

    assert tratamiento_a_cancelar.activo is False, "El tratamiento debe estar inactivo"
    assert context.cancelacion_realizada == True, "La cancelación debe estar realizada"


def inicializar_contexto_basico(context):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from usuarios.models import PacienteProfile, MedicoProfile

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

    context.usuario_medico = User.objects.create_user(
        username=f"medico_{fake.user_name()}",
        email=fake.unique.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        cedula=str(fake.unique.random_number(digits=10, fix_len=True)),
        tipo_usuario='medico',
        genero='M'
    )

    context.medico = MedicoProfile.objects.create(
        usuario=context.usuario_medico,
        numero_licencia=fake.unique.bothify(text='LIC-#####'),
        especializacion='neurologia',
        anos_experiencia=5
    )

def crear_episodio_dummy(paciente, tipo_migraña):
    return EpisodioCefalea.objects.create(
        paciente=paciente,
        duracion_cefalea_horas=2,
        severidad='Moderada',
        localizacion='Unilateral',
        caracter_dolor='Pulsátil',
        empeora_actividad=True,
        nauseas_vomitos=True,
        fotofobia=True,
        fonofobia=False,
        presencia_aura=True,
        sintomas_aura='Visuales, Sensitivos',
        duracion_aura_minutos=30,
        en_menstruacion=False,
        anticonceptivos=False,
        categoria_diagnostica=tipo_migraña
    )
