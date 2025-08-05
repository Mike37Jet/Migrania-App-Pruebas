# language: es
# Created by Lema Dayana, López Paula, Damarys Oña, Proaño Juan at 7/7/2025

Característica: Generación y análisis de seguimiento de tratamiento médico

  Como médico
  Quiero saber la información médica del paciente
  Para crear un tratamiento médico que mejore la calidad de vida del paciente
  Y sea personalizado según la categorización (migraña sin aura, migraña con aura, cefalea de tipo tensional)

  Antecedentes:
    Dado que el paciente tiene al menos un historial de migrañas

  Esquema del escenario: Generar tratamiento según tipo de migraña

    Dado que el paciente presenta su primer episodio con la categorización <tipo_migraña>
    Cuando el médico ingresa los datos del tratamiento
      | Campo                |
      | Dosis                |
      | Medicamento          |
      | Características      |
      | Frecuencia           |
      | Duración tratamiento |
      | Recomendacion        |
    Entonces el sistema crea el tratamiento


    Ejemplos:
      | tipo_migraña              |
      | Migraña sin aura          |
      | Migraña con aura          |
      | Cefalea de tipo tensional |


  Esquema del escenario: Seguimiento de tratamiento con cumplimiento alto

    Dado que el paciente tiene un tratamiento activo correspondiente a un episodio médico
    Y el historial de alertas indica que el paciente ha confirmado <porcentaje_cumplimiento>% de las tomas correspondientes a <numero_tratamientos> tratamientos
    Cuando el médico evalúa el cumplimiento del tratamiento anterior
    Entonces se decide modificar el tratamiento
    Y el médico ingresa las siguientes características para el nuevo tratamiento
      | Cantidad             |
      | Medicación           |
      | Características      |
      | Frecuencia           |
      | Duración tratamiento |
      | Recomendación        |
    Y el sistema debe actualizar el tratamiento con los nuevos datos

    Ejemplos:
      | porcentaje_cumplimiento | numero_tratamientos |
      | 85                      | 1                   |

  Esquema del escenario: Seguimiento de tratamiento con bajo cumplimiento

    Dado que el paciente tiene un tratamiento activo correspondiente a un episodio médico
    Y el historial de alertas indica que el paciente ha confirmado <porcentaje_cumplimiento>% de las tomas correspondientes a <numero_tratamientos> tratamientos
    Cuando el médico evalúa el cumplimiento del tratamiento anterior
    Entonces se decide cancelar el tratamiento
    Y el médico ingresa el motivo como "<motivo_cancelacion>"
    Y el sistema debe cancelar el tratamiento con los datos ingresados


    Ejemplos:
      | porcentaje_cumplimiento | numero_tratamientos | motivo_cancelacion            |
      | 60                      | 1                   | Incumplimiento de tratamiento |
