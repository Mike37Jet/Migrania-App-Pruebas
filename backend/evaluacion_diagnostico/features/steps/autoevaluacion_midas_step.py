import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migraine_app.settings')
django.setup()

from datetime import datetime

from behave import *

from usuarios.repositories import FakeUserRepository
from evaluacion_diagnostico.repositories import FakeAutoevaluacionMidasRepository
from evaluacion_diagnostico.autoevaluacion_midas_service import AutoevaluacionMidasService
from django.core.exceptions import ValidationError

use_step_matcher("re")


@step('que el paciente ha realizado una autoevaluación en la fecha "(?P<fecha_ultima_autoevaluacion>.+)"')
def step_impl(context, fecha_ultima_autoevaluacion):
    # 1. Preparar repositorios en memoria para una prueba aislada
    user_repo = FakeUserRepository()
    autoevaluacion_repo = FakeAutoevaluacionMidasRepository()
    context.autoevaluacion_repo = autoevaluacion_repo
    # 2. Inyectar el repositorio FAKE en el servicio para desacoplar la lógica
    context.autoevaluacion_service = AutoevaluacionMidasService(repository=autoevaluacion_repo)

    # 3. Crear un paciente de prueba para asociar el episodio.
    user_data = {
        'username': "pepe",
        'email': "pepe@test.com",
        'password': 'abc123',
        'first_name': 'Pepe',
        'last_name': 'Perez'
    }

    # Aunque no necesitemos datos de perfil para esta prueba, el método espera el diccionario.
    profile_data = {
        'contacto_emergencia_nombre': 'Juanita Burbano',
        'contacto_emergencia_telefono': '0992675567',
        'contacto_emergencia_relacion': '0992673389'
    }

    context.paciente = user_repo.create_paciente(user_data, profile_data)

    # Registrar la autoevaluación inicial
    fecha = datetime.fromisoformat(fecha_ultima_autoevaluacion)
    context.autoevaluacion_service.iniciar_autoevaluacion_para(context.paciente, fecha)


@step('el paciente intenta realizar una nueva autoevaluación en la fecha "(?P<fecha_nueva_autoevaluacion>.+)"')
def step_impl(context, fecha_nueva_autoevaluacion):

    fecha = datetime.fromisoformat(fecha_nueva_autoevaluacion)
    context.nueva_evaluacion = context.autoevaluacion_service.iniciar_autoevaluacion_para(context.paciente, fecha)


@step("la nueva autoevaluación se registrará")
def step_impl(context):
    assert context.autoevaluacion_repo.obtener_ultima_autoevaluacion(context.paciente) is context.nueva_evaluacion


@step("la nueva autoevaluación no se registrará")
def step_impl(context):
    assert context.autoevaluacion_repo.obtener_ultima_autoevaluacion(context.paciente) is not context.nueva_evaluacion
