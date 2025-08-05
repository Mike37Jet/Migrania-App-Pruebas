# language: es

Característica: Autoevaluación MIDAS
  Como paciente
  Quiero saber mi grado de discapacidad
  Para entender mejor el impacto de migrañas en mi vida diaria

  Esquema del escenario: La evaluación está disponible si han pasado al menos 3 meses
    Dado que el paciente ha realizado una autoevaluación en la fecha "<fecha_ultima_autoevaluacion>"
    Cuando el paciente intenta realizar una nueva autoevaluación en la fecha "<fecha_nueva_autoevaluacion>"
    Entonces la nueva autoevaluación se registrará

    Ejemplos:
      | fecha_ultima_autoevaluacion | fecha_nueva_autoevaluacion |
      | 2025-01-01                  | 2025-04-01                 |
      | 2025-03-01                  | 2025-06-01                 |


  Esquema del escenario: La evaluación no está disponible si no han pasado al menos 3 meses
    Dado que el paciente ha realizado una autoevaluación en la fecha "<fecha_ultima_autoevaluacion>"
    Cuando el paciente intenta realizar una nueva autoevaluación en la fecha "<fecha_nueva_autoevaluacion>"
    Entonces la nueva autoevaluación no se registrará

    Ejemplos:
      | fecha_ultima_autoevaluacion | fecha_nueva_autoevaluacion |
      | 2024-01-01                  | 2024-03-01                 |
      | 2024-03-01                  | 2024-04-01                 |