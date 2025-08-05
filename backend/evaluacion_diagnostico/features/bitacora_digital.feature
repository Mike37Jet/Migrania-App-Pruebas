#language: es

Característica: Bitácora digital de episodios de cefalea.
  Como medico
  Quiero identificar el tipo o subtipo de cefalea a partir de la bitácora de episodios del paciente
  Para facilitar la precisión del diagnóstico de migraña del paciente.

  Esquema del escenario: Categorización de un episodio de cefalea basado en los síntomas registrados en pacientes
    Dado que un paciente ha ingresado datos para un nuevo episodio de cefalea con las siguientes características
      | Característica           | Valor                    |
      | Duración Cefalea (horas) | <duracion_cefalea_horas> |
      | Severidad del Dolor      | <severidad>              |
      | Localización del Dolor   | <localizacion>           |
      | Carácter del Dolor       | <caracter_dolor>         |
      | Empeora con Actividad    | <empeora_actividad>      |
      | Náuseas o Vómitos        | <nauseas_vomitos>        |
      | Sensibilidad a la Luz    | <fotofobia>              |
      | Sensibilidad al Sonido   | <fonofobia>              |
      | Presencia de Aura        | <presencia_aura>         |
      | Síntomas del Aura        | <sintomas_aura>          |
      | Duración del Aura (min)  | <duracion_aura_minutos>  |
      | En menstruación          | <en_menstruacion>        |
      | Anticonceptivos          | <anticonceptivos>        |
    Cuando todos los datos estén completos,
    Entonces el sistema debe categorizar el episodio como "<categoria_esperada>",
    Y el episodio se guarda en la bitácora del paciente
    Ejemplos:
      | categoria_esperada        | duracion_cefalea_horas | severidad | localizacion | caracter_dolor | empeora_actividad | nauseas_vomitos | fotofobia | fonofobia | presencia_aura | sintomas_aura        | duracion_aura_minutos | en_menstruacion | anticonceptivos |
      | Migraña sin aura          | 6                      | Severa    | Unilateral   | Pulsátil       | Sí                | Sí              | Sí        | Sí        | No             | Ninguno              | 0                     | Si              | Si              |
      | Migraña con aura          | 4                      | Moderada  | Unilateral   | Pulsátil       | Sí                | No              | Sí        | Sí        | Sí             | Visuales, Sensitivos | 30                    | Si              | Si              |
      | Cefalea de tipo tensional | 2                      | Leve      | Bilateral    | Opresivo       | No                | No              | No        | Sí        | No             | Ninguno              | 0                     | No              | No              |
