# language: es

Característica: Análisis de patrones en episodios de cefalea
  Como paciente que sufre cefaleas
  Quiero identificar semanalmente los patrones que se repiten en mis episodios
  Para prevenir nuevas crisis y mejorar el diálogo con mi doctor.

Esquema del escenario: Análisis de características diagnósticas clave
    Dado que el paciente ha registrado los siguientes episodios
      | localizacion | caracter_dolor | empeora_actividad |
      | "Unilateral" | "Pulsátil"     | "Sí"              |
      | "Bilateral"  | "Opresivo"     | "No"              |
      | "Unilateral" | "Pulsátil"     | "Sí"              |
      | "Unilateral" | "Pulsátil"     | "No"              |
      | "Unilateral" | "Pulsátil"     | "Sí"              |
      | "Unilateral" | "Pulsátil"     | "Sí"              |
      | "Unilateral" | "Pulsátil"     | "Sí"              |
      | "Bilateral"  | "Opresivo"     | "No"              |
      | "Unilateral" | "Pulsátil"     | "Sí"              |
    Cuando se analiza las características diagnósticas principales
    Entonces el sistema debe generar una conclusión sobre patrones clínicos con el mensaje: "<mensaje_conclusion>"

    Ejemplos:
      | mensaje_conclusion                                                                                                                              |
      | "Se ha detectado un patrón clínico muy consistente. Tus episodios casi siempre son unilaterales, de carácter pulsátil y se agravan con la actividad física. Estas son características típicas de la migraña." |

Esquema del escenario: Análisis de síntomas asociados y su frecuencia
    Dado que el paciente ha registrado los siguientes episodios
      | severidad  | nauseas_vomitos | fotofobia | fonofobia |
      | "Severa"   | "Sí"            | "No"      | "Sí"      |
      | "Moderada" | "No"            | "Sí"      | "Sí"      |
      | "Leve"     | "No"            | "No"      | "No"      |
      | "Severa"   | "Sí"            | "Sí"      | "Sí"      |
      | "Severa"   | "Sí"            | "No"      | "Sí"      |
      | "Moderada" | "No"            | "Sí"      | "Sí"      |
      | "Severa"   | "No"            | "No"      | "Sí"      |
      | "Moderada" | "No"            | "Sí"      | "No"      |
      | "Severa"   | "Sí"            | "No"      | "Sí"      |
    Cuando se analiza la frecuencia y correlación de los síntomas asociados
    Entonces el sistema debe generar una conclusión sobre el síntoma más frecuente con el mensaje: "<mensaje_sintoma_frecuente>"
    Y el sistema debe generar una conclusión sobre la correlación con la severidad con el mensaje: "<mensaje_correlacion_severidad>"

    Ejemplos:
      | mensaje_sintoma_frecuente                                                           | mensaje_correlacion_severidad                                                                                                   |
      | "Se observa que la fonofobia (sensibilidad al sonido) es un síntoma constante en tus crisis." | "Parece haber una relación entre la intensidad del dolor y las náuseas: cuando la cefalea es 'Severa', es más probable que experimentes náuseas." |

Esquema del escenario: Análisis del fenómeno del aura
    Dado que el paciente ha registrado los siguientes episodios
      | categoria_esperada | presencia_aura | sintomas_aura | duracion_aura_minutos |
      | "Migraña sin aura" | "No"           | "Ninguno"     | 0                     |
      | "Migraña sin aura" | "No"           | "Ninguno"     | 0                     |
      | "Migraña con aura" | "Sí"           | "Visuales"    | 25                    |
      | "Migraña sin aura" | "No"           | "Ninguno"     | 0                     |
      | "Migraña con aura" | "Sí"           | "Sensoriales" | 15                    |
      | "Migraña sin aura" | "No"           | "Ninguno"     | 0                     |
      | "Migraña con aura" | "Sí"           | "Visuales"    | 30                    |
      | "Migraña sin aura" | "No"           | "Ninguno"     | 0                     |
      | "Migraña con aura" | "Sí"           | "Visuales"    | 20                    |
    Cuando se analizan y clasifican los episodios relacionados con el aura
    Entonces el sistema debe generar una conclusión detallada sobre el aura con el mensaje: "<mensaje_aura>"

    Ejemplos:
      | mensaje_aura                                                                                                                                                                                                     |
      | "Tu bitácora muestra que experimentas dos tipos de crisis: migrañas sin aura y migrañas con aura. Cuando tienes un aura, suele ser de tipo visual (o sensorial) y durar aproximadamente entre 15 y 30 minutos." |

Esquema del escenario: Detección de patrones de recurrencia en días de la semana
    Dado que el paciente ha registrado los siguientes episodios
      | dia         | categoria_esperada          |
      | "Lunes"     | "Migraña sin aura"          |
      | "Martes"    | "Cefalea de tipo tensional" |
      | "Viernes"   | "Migraña con aura"          |
      | "Sábado"    | "Migraña sin aura"          |
      | "Viernes"   | "Migraña sin aura"          |
      | "Lunes"     | "Migraña sin aura"          |
      | "Miércoles" | "Cefalea de tipo tensional" |
      | "Viernes"   | "Migraña sin aura"          |
      | "Viernes"   | "Migraña sin aura"          |
      | "Lunes"     | "Migraña con aura"          |
      | "Jueves"    | "Migraña sin aura"          |
    Cuando se analiza la recurrencia semanal de los episodios
    Entonces el sistema debe generar una alerta de patrón semanal para los siguientes días: <dias_recurrentes>
    Y se sugiere analizar las rutinas o posibles factores asociados a esos días para identificar la causa

    Ejemplos:
      | dias_recurrentes |
      | "Viernes, Lunes" |


Esquema del escenario: Detección de un posible patrón de migraña menstrual
    Dado que el paciente ha registrado los siguientes episodios
      | categoria_esperada | severidad  | en_menstruacion | anticonceptivos |
      | "Migraña sin aura" | "Severa"   | "Sí"            | "Sí"              |
      | "Migraña sin aura" | "Moderada" | "No"            | "Sí"              |
      | "Migraña con aura" | "Severa"   | "Sí"            | "Sí"              |
      | "Migraña sin aura" | "Moderada" | "No"            | "Sí"              |
      | "Migraña sin aura" | "Severa"   | "Sí"            | "Sí"              |
      | "Migraña con aura" | "Severa"   | "Sí"            | "Sí"              |
      | "Cefalea tensional"| "Leve"     | "No"            | "Sí"              |
      | "Migraña sin aura" | "Moderada" | "Sí"            | "Sí"              |
    Cuando el sistema analiza la relación entre los episodios y el ciclo menstrual
    Entonces el sistema debe generar una conclusión específica sobre el patrón hormonal con el mensaje: "<mensaje_conclusion_hormonal>"

    Ejemplos:
      | mensaje_conclusion_hormonal                                                                                                                                                                             |
      | "Hemos detectado que una parte significativa de tus episodios de migraña ocurren durante tu menstruación. Esto podría indicar un patrón de 'migraña menstrual'. Te recomendamos conversar sobre este patrón con tu médico." |