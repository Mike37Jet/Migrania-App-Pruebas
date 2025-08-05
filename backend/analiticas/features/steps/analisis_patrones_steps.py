from behave import *

use_step_matcher("re")


@given("que el paciente ha registrado los siguientes episodios")
def step_impl(context):
    from usuarios.repositories import FakeUserRepository
    from analiticas.repositories import FakeAnalisisPatronesRepository
    from analiticas.services import AnalisisPatronesService
    from analiticas.analisis_patrones_data_structures import EpisodioData

    user_repo = FakeUserRepository()
    context.analisis_repo = FakeAnalisisPatronesRepository()
    context.analisis_service = AnalisisPatronesService(repository=context.analisis_repo)

    user_data = {
        'username': "pacienteAnalisis", 'email': "paciente.analisis@test.com",
        'password': 'testpassword123', 'first_name': 'Ana', 'last_name': 'Lisis', 'genero': 'F'
    }
    profile_data = {}

    context.paciente = user_repo.create_paciente(user_data, profile_data)
    assert context.paciente is not None, "La creación del paciente de prueba falló."

    for row in context.table:
        row_data = {k: v.strip('"') for k, v in row.as_dict().items()}

        if 'categoria_esperada' in row_data:
            row_data['categoria_diagnostica'] = row_data.pop('categoria_esperada')

        episodio_data = EpisodioData(**row_data)
        episodio_data.paciente_id = context.paciente.pk
        context.analisis_repo.guardar_episodio(context.paciente.pk, episodio_data)

    episodios_guardados = len(context.analisis_repo.obtener_episodios_por_paciente(context.paciente.pk))
    episodios_esperados = len(context.table.rows)
    assert episodios_guardados == episodios_esperados, \
        f"Se esperaban {episodios_esperados} episodios, pero se guardaron {episodios_guardados}."


@when("se analiza las características diagnósticas principales")
def step_impl(context):
    context.conclusion_clinica = context.analisis_service.analizar_patrones_clinicos(context.paciente.pk)
    assert context.conclusion_clinica is not None, "El servicio no devolvió una conclusión clínica."


@when("se analiza la frecuencia y correlación de los síntomas asociados")
def step_impl(context):
    context.conclusiones_sintomas = context.analisis_service.analizar_frecuencia_sintomas(context.paciente.pk)
    assert context.conclusiones_sintomas is not None, "El servicio no devolvió un diccionario de conclusiones de síntomas."


@when("se analizan y clasifican los episodios relacionados con el aura")
def step_impl(context):
    context.conclusion_aura = context.analisis_service.analizar_patrones_aura(context.paciente.pk)
    assert context.conclusion_aura is not None, "El servicio no devolvió una conclusión sobre el aura."


@when("se analiza la recurrencia semanal de los episodios")
def step_impl(context):
    context.dias_recurrentes = context.analisis_service.analizar_recurrencia_semanal(context.paciente.pk)
    assert context.dias_recurrentes is not None, "El servicio no devolvió una lista de días recurrentes."


@when("el sistema analiza la relación entre los episodios y el ciclo menstrual")
def step_impl(context):
    context.conclusion_hormonal = context.analisis_service.analizar_patron_menstrual(context.paciente.pk)
    assert context.conclusion_hormonal is not None, "El servicio no devolvió una conclusión hormonal."


@then('el sistema debe generar una conclusión sobre patrones clínicos con el mensaje: "(?P<mensaje_conclusion>.+)"')
def step_impl(context, mensaje_conclusion):
    valor_esperado = mensaje_conclusion.strip('"')
    assert context.conclusion_clinica == valor_esperado, \
        f"Esperado: '{valor_esperado}', Obtenido: '{context.conclusion_clinica}'"


@then(
    'el sistema debe generar una conclusión sobre el síntoma más frecuente con el mensaje: "(?P<mensaje_sintoma_frecuente>.+)"')
def step_impl(context, mensaje_sintoma_frecuente):
    valor_esperado = mensaje_sintoma_frecuente.strip('"')
    conclusion_obtenida = context.conclusiones_sintomas.get('sintoma_frecuente')
    assert conclusion_obtenida == valor_esperado, \
        f"Esperado: '{valor_esperado}', Obtenido: '{conclusion_obtenida}'"


@then(
    'el sistema debe generar una conclusión sobre la correlación con la severidad con el mensaje: "(?P<mensaje_correlacion_severidad>.+)"')
def step_impl(context, mensaje_correlacion_severidad):
    valor_esperado = mensaje_correlacion_severidad.strip('"')
    conclusion_obtenida = context.conclusiones_sintomas.get('correlacion_severidad')
    assert conclusion_obtenida == valor_esperado, \
        f"Esperado: '{valor_esperado}', Obtenido: '{conclusion_obtenida}'"


@then('el sistema debe generar una conclusión detallada sobre el aura con el mensaje: "(?P<mensaje_aura>.+)"')
def step_impl(context, mensaje_aura):
    valor_esperado = mensaje_aura.strip('"')
    assert context.conclusion_aura == valor_esperado, \
        f"Esperado: '{valor_esperado}', Obtenido: '{context.conclusion_aura}'"


@then('el sistema debe generar una alerta de patrón semanal para los siguientes días: "(?P<dias_recurrentes>.+)"')
def step_impl(context, dias_recurrentes):
    dias_esperados_set = set(dias_recurrentes.strip('"').split(', '))
    dias_obtenidos_set = set(context.dias_recurrentes)

    assert dias_obtenidos_set == dias_esperados_set, \
        f"Esperado: {sorted(list(dias_esperados_set))}, Obtenido: {sorted(list(dias_obtenidos_set))}"


@then("se sugiere analizar las rutinas o posibles factores asociados a esos días para identificar la causa")
def step_impl(context):
    assert True, "Este es un paso descriptivo y siempre debe pasar."


@then(
    'el sistema debe generar una conclusión específica sobre el patrón hormonal con el mensaje: "(?P<mensaje_conclusion_hormonal>.+)"')
def step_impl(context, mensaje_conclusion_hormonal):
    valor_esperado = mensaje_conclusion_hormonal.strip('"')
    assert context.conclusion_hormonal == valor_esperado, \
        f"Esperado: '{valor_esperado}', Obtenido: '{context.conclusion_hormonal}'"
