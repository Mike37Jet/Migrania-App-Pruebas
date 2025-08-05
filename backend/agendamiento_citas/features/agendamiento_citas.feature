# Created by marce at 29/7/2025
#language: es

Característica: : Agendamiento de citas medicas
  Como paciente,
  quiero agendar una cita médica con un doctor disponible,
  para recibir atención médica en el momento más conveniente.


  Esquema del escenario: Solicitar una cita médica
  Dado que hay disponibilidad con el <doctor> con <cedula_doctor> el <fecha_cita> a las <hora_cita>
  Cuando <nombre_paciente> con <cedula_paciente> agenda una cita
  Entonces el paciente recibe un recordatorio para el <fecha_recordatorio> a las <hora_recordatorio>
  Ejemplos:
    | nombre_paciente |  doctor     | cedula_doctor    |cedula_paciente| fecha_cita | hora_cita | fecha_recordatorio | hora_recordatorio |
    | Laura Gómez     |  Dr. Salas  |  1716852634      | 1716526263    |2025-09-18 | 09:00     | 2025-10-17         | 09:00  |


Escenario: Solicitar atención médica urgente por MIDAS
    Dado que el paciente con cedula "1755236545" presenta discapacidad severa
    Cuando el paciente agenda una atención medica urgente
    Entonces se asigna un doctor disponible inmediatamente

Esquema del escenario: Reagendar una cita por parte del paciente
    Dado que <nombre_paciente> con <cedula_paciente> tiene una cita agendada con el doctor <doctor> con <cedula_doctor> el <fecha_original> a las <hora_original>
    Cuando solicita una reprogramación para <fecha_nueva> con al menos 24 horas de anticipación
    Entonces se sugiere automáticamente un horario alternativo disponible
    Y se reorganiza la cita
      Ejemplos:
        | nombre_paciente |cedula_paciente |doctor     |cedula_doctor| fecha_original | hora_original | fecha_nueva |
        | Laura Gómez      | 1716526263    |Dr. Salas | 1716852634 |2025-09-18     | 09:00         | 2025-10-25     |
