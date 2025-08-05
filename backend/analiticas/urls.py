# analiticas/urls.py
from django.urls import path
from .views import AnalisisPatronesView, EstadisticasHistorialView, PromedioSemanalView

urlpatterns = [
    path('patrones/', AnalisisPatronesView.as_view(), name='analisis-patrones'),
    path('estadisticas/', EstadisticasHistorialView.as_view(), name='estadisticas-historial'),
    path('promedio-semanal/', PromedioSemanalView.as_view(), name='promedio-semanal'),
]