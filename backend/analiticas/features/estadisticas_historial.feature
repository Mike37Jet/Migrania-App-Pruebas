# Created by Dorian at 18/7/2025
# language: es

Característica: Estadística e historial
  Como médico,
  Quiero acceder al historial clínico y estadísticas detalladas relacionadas con episodios de migraña de mis pacientes o posibles pacientes,
  Para personalizar el tratamiento y apoyar el diagnóstico de manera efectiva.

  Antecedentes:
  Dado que el paciente tiene al menos tres episodios registrados en su bitácora digital
  Y cuenta al menos tres evaluaciones MIDAS completadas

  @promedio_semanal
  Esquema del escenario: Análisis del promedio semanal de episodios de migraña
  Dado que el paciente tiene <total_episodios> episodios registrados en su bitácora digital
  Y el primer episodio fue registrado en la fecha <fecha_inicio>
  Y el último episodio fue registrado en la fecha <fecha_fin>
  Cuando solicito el análisis del promedio semanal
  Entonces el sistema mostrará que el promedio semanal de episodios es <promedio_semanal> veces
Ejemplos:
  | total_episodios | fecha_inicio | fecha_fin  | promedio_semanal  |
  | 28              | 2024-01-01   | 2024-02-26 | 3.5               |
  | 14              | 2024-05-01   | 2024-06-19 | 2.0               |

  @duracion_promedio
  Esquema del escenario: Análisis de duración promedio por episodio de migraña
  Dado que el paciente tiene <total_episodios> episodios registrados en su bitácora digital
  Y la suma total de duración de todos los episodios es de <suma_duracion_total> horas
  Cuando solicito el análisis de duración promedio
  Entonces el sistema mostrará que la duración promedio por episodio es de <duracion_promedio> horas
Ejemplos:
  | total_episodios | suma_duracion_total | duracion_promedio |
  | 10              | 25                  | 2.5               |
  | 8               | 16                  | 2.0               |

  @intensidad_promedio
  Esquema del escenario: Cálculo de intensidad promedio del dolor en episodios de migraña
  Dado que el paciente tiene episodios registrados en su bitácora digital
  Cuando solicito el análisis de intensidad de dolores promedio
  Entonces el sistema mostrará la intensidad promedio es <intensidad_promedio>
Ejemplos:
  | intensidad_promedio  |
  | Moderado             |
  | Severo               |
  | Leve                 |

  @asociacion_hormonal
  Esquema del escenario: Análisis de episodios asociados a menstruación y anticonceptivos
  Dado que el paciente tiene <total_episodios> episodios registrados en su bitácora digital
  Y <episodios_menstruacion> episodios ocurrieron durante la menstruación
  Y <episodios_anticonceptivos> episodios están asociados al uso de anticonceptivos
  Cuando solicito el análisis de asociación hormonal
  Entonces el sistema mostrará que el <porcentaje_menstruacion>% de los episodios ocurrieron durante la menstruación
  Y mostrará que el <porcentaje_anticonceptivos>% de los episodios están asociados al uso de anticonceptivos
Ejemplos:
  | total_episodios | episodios_menstruacion | episodios_anticonceptivos | porcentaje_menstruacion | porcentaje_anticonceptivos |
  | 50              | 20                     | 15                        | 40%                     | 30%                       |
  | 30              | 10                     | 12                        | 33.3%                   | 40%                       |

  @evolucion_midas
  Esquema del escenario: Evolución de la autoevaluación MIDAS
  Dado que el paciente tiene un promedio de puntuación MIDAS de <puntuacion_promedio> puntos
  Y en la evaluación MIDAS más reciente tuvo una puntuación de <puntuacion_actual> puntos
  Cuando solicito el análisis de evolución de discapacidad
  Entonces el sistema mostrará que la variación en la puntuación MIDAS es de <variacion_puntaje_midas> puntos
  Y mostrará que la discapacidad del paciente ha <tendencia_de_discapacidad>
  Ejemplos:
    | puntuacion_promedio | puntuacion_actual | variacion_puntaje_midas | tendencia_de_discapacidad|
    | 20                  | 15                | -5                      | "Mejorado"               |
    | 15                  | 22                | 7                       | "Empeorado"              |