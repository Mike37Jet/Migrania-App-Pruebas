# analiticas/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404
from datetime import datetime

from .services import AnalisisPatronesService
from .repositories import DjangoAnalisisPatronesRepository
from .serializers import AnalisisPatronesSerializer
from .estadisticas_service import EstadisticasHistorialService
from .estadisticas_serializers import EstadisticasHistorialSerializer, PromediaSemanalRequestSerializer
from usuarios.models import Usuario


class AnalisisPatronesView(APIView):
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden ver su análisis

    def get(self, request, *args, **kwargs):
        # 1. Obtener el ID del paciente del usuario autenticado
        paciente_id = request.user.pk

        # 2. Inyectar el repositorio REAL en el servicio
        repo = DjangoAnalisisPatronesRepository()
        servicio_analisis = AnalisisPatronesService(repository=repo)

        # 3. Ejecutar todos los métodos de análisis
        resultados = {
            "conclusion_clinica": servicio_analisis.analizar_patrones_clinicos(paciente_id),
            "conclusiones_sintomas": servicio_analisis.analizar_frecuencia_sintomas(paciente_id),
            "conclusion_aura": servicio_analisis.analizar_patrones_aura(paciente_id),
            "dias_recurrentes": servicio_analisis.analizar_recurrencia_semanal(paciente_id),
            "conclusion_hormonal": servicio_analisis.analizar_patron_menstrual(paciente_id),
        }

        # 4. Usar el serializador para formatear la respuesta
        serializer = AnalisisPatronesSerializer(data=resultados)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class EstadisticasHistorialView(APIView):
    """
    API View para estadísticas del historial de episodios de bitácora digital.
    
    Endpoints:
    - GET /api/analiticas/estadisticas/ - Estadísticas del usuario actual (paciente)
    - GET /api/analiticas/estadisticas/?paciente_id=X - Estadísticas de paciente específico (personal médico)
    """
    permission_classes = [IsAuthenticated]

    def get_paciente_id(self, request):
        """
        Obtiene el ID del paciente según el rol del usuario.
        """
        user = request.user
        
        # Si es personal médico, puede consultar paciente específico
        if user.es_medico or user.es_enfermera:
            paciente_id = request.query_params.get('paciente_id')
            if paciente_id:
                # Verificar que el paciente existe
                try:
                    paciente = Usuario.objects.get(id=paciente_id, tipo_usuario=Usuario.TipoUsuario.PACIENTE)
                    return paciente.id
                except Usuario.DoesNotExist:
                    raise Http404("Paciente no encontrado")
            else:
                # Si no especifica paciente, retornar error
                return None
        
        # Si es paciente, solo puede ver sus propias estadísticas
        elif user.es_paciente:
            return user.id
        
        # Otros roles no tienen acceso
        else:
            return None

    def get(self, request, *args, **kwargs):
        """
        Obtiene las estadísticas del historial de episodios de bitácora digital.
        """
        paciente_id = self.get_paciente_id(request)
        
        if paciente_id is None:
            if request.user.es_medico or request.user.es_enfermera:
                return Response(
                    {"error": "Debe especificar el parámetro 'paciente_id' para consultar estadísticas"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "No tiene permisos para acceder a estadísticas"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Inicializar el servicio de estadísticas
        repo = DjangoAnalisisPatronesRepository()
        servicio_estadisticas = EstadisticasHistorialService(repository=repo)

        # Validar que el paciente tenga episodios mínimos
        if not servicio_estadisticas.validar_episodios_minimos(paciente_id):
            return Response(
                {"error": "El paciente debe tener al menos 3 episodios registrados para generar estadísticas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener todas las estadísticas de bitácora digital
        resultados = {}
        
        # 1. Duración promedio
        duracion_promedio = servicio_estadisticas.calcular_duracion_promedio(paciente_id)
        if duracion_promedio > 0:
            resultados["duracion_promedio"] = duracion_promedio
        
        # 2. Intensidad promedio
        intensidad_promedio = servicio_estadisticas.calcular_intensidad_promedio(paciente_id)
        if intensidad_promedio != "No hay datos":
            resultados["intensidad_promedio"] = intensidad_promedio
        
        # 3. Análisis hormonal
        porcentajes_hormonales = servicio_estadisticas.calcular_porcentajes_hormonales(paciente_id)
        resultados["porcentaje_menstruacion"] = porcentajes_hormonales["menstruacion"]
        resultados["porcentaje_anticonceptivos"] = porcentajes_hormonales["anticonceptivos"]
        
        # 4. Información general de episodios
        episodios = repo.obtener_episodios_por_paciente(paciente_id)
        if episodios:
            resultados["total_episodios"] = len(episodios)
            resultados["fecha_primer_episodio"] = min(ep.fecha_creacion for ep in episodios).date()
            resultados["fecha_ultimo_episodio"] = max(ep.fecha_creacion for ep in episodios).date()

        # Serializar y retornar respuesta
        serializer = EstadisticasHistorialSerializer(data=resultados)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)


class PromedioSemanalView(APIView):
    """
    API View para el cálculo de promedio semanal de episodios.
    
    Endpoints:
    - GET /api/analiticas/promedio-semanal/ - Promedio semanal del usuario actual
    - GET /api/analiticas/promedio-semanal/?paciente_id=X&fecha_inicio=Y&fecha_fin=Z
    """
    permission_classes = [IsAuthenticated]

    def get_paciente_id(self, request):
        """
        Obtiene el ID del paciente según el rol del usuario.
        """
        user = request.user
        
        if user.es_medico or user.es_enfermera:
            paciente_id = request.query_params.get('paciente_id')
            if paciente_id:
                try:
                    paciente = Usuario.objects.get(id=paciente_id, tipo_usuario=Usuario.TipoUsuario.PACIENTE)
                    return paciente.id
                except Usuario.DoesNotExist:
                    raise Http404("Paciente no encontrado")
            return None
        elif user.es_paciente:
            return user.id
        else:
            return None

    def get(self, request, *args, **kwargs):
        """
        Calcula el promedio semanal de episodios en un período específico.
        """
        paciente_id = self.get_paciente_id(request)
        
        if paciente_id is None:
            if request.user.es_medico or request.user.es_enfermera:
                return Response(
                    {"error": "Debe especificar el parámetro 'paciente_id'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "No tiene permisos para acceder a estadísticas"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Validar parámetros de fecha
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')
        
        if not fecha_inicio_str or not fecha_fin_str:
            return Response(
                {"error": "Debe especificar 'fecha_inicio' y 'fecha_fin' en formato YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Inicializar servicio y calcular promedio semanal
        repo = DjangoAnalisisPatronesRepository()
        servicio_estadisticas = EstadisticasHistorialService(repository=repo)
        
        promedio_semanal = servicio_estadisticas.calcular_promedio_semanal(
            paciente_id, fecha_inicio, fecha_fin
        )
        
        return Response({
            "promedio_semanal": promedio_semanal,
            "fecha_inicio": fecha_inicio.date(),
            "fecha_fin": fecha_fin.date(),
            "paciente_id": paciente_id
        })