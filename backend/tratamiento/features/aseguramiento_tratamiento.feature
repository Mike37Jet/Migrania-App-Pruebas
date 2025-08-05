# Created by Escobar Alex, Haro Rodrigo, Jacome Emilio, Mendosa Miguel at 22/7/2025
# language: es

Característica: Aseguramiento del tratamiento para la migraña
  Como paciente con tratamiento para la migraña,
  Quiero recordar las actividades definidas,
  Para cumplirlas y minimizar interrupciones en mi vida diaria.

  Antecedentes:
    Dado que el paciente tiene una medicina prescrita para la migraña
  # MEDICAMENTOS
    ## Recordatorio
  Escenario: Recordatorio de toma de medicamentos pendientes
    Cuando la hora actual sea 30 minutos antes de la hora de la toma
    Entonces se enviará un recordatorio al paciente indicando que debe tomar su medicación pronto
    Y el estado del recordatorio será "activo"

    ## Alerta
  Esquema del escenario: Alerta de toma de medicamentos sin confirmar
    Dado que el paciente ha recibido una <numero_alerta> alerta para tomar su medicación
    Y la hora actual es <tiempo_transcurrido> minutos después de la hora programada para la toma
    Cuando transcurran 15 minutos sin que el paciente confirme la toma
    Entonces se actualizará el estado de la alerta a "sin confirmar"
    Y se programará una <accion_siguiente> alerta

    Ejemplos:
      | numero_alerta | tiempo_transcurrido | accion_siguiente |
      | primera       | 0                   | segunda          |
      | segunda       | 30                  | tercera          |
      | tercera       | 45                  | ninguna          |

  Esquema del escenario: Alerta de toma de medicamentos confirmada
    Dado que el paciente ha recibido una <numero_alerta> alerta para tomar su medicación
    Y la hora actual es <tiempo_transcurrido> minutos después de la hora programada para la toma
    Cuando el paciente confirma que <estado_toma> ha tomado la medicación
    Entonces se actualizará el estado de la alerta a "<estado_resultado>"

    Ejemplos:
      | numero_alerta | tiempo_transcurrido | estado_toma | estado_resultado |
      | primera       | 0                   | si          | tomado           |
      | primera       | 0                   | no          | no tomado        |
      | segunda       | 30                  | si          | tomado tarde     |
      | segunda       | 30                  | no          | no tomado        |
      | tercera       | 45                  | si          | tomado muy tarde |
      | tercera       | 45                  | no          | no tomado        |

  # RECOMENDACIONES
    ## Recordatorio
  Escenario: Recordatorio de recomendación de tratamiento
    Dado que el paciente tiene una recomendación de tratamiento para la migraña
    Cuando sea las 9 horas del día
    Entonces se notificará mediante un recordatorio sugiriéndole seguir esta recomendación
    Y el estado de la recordatorio será "activo"
