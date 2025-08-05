# evaluacion_diagnostico/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PreguntaViewSet, AutoevaluacionMidasViewSet, RespuestaViewSet, EpisodioCefaleaViewSet

router = DefaultRouter()
router.register(r'evaluaciones/preguntas', PreguntaViewSet, basename='pregunta')
router.register(r'evaluaciones/autoevaluaciones', AutoevaluacionMidasViewSet, basename='autoevaluacion')
router.register(r'evaluaciones/respuestas', RespuestaViewSet, basename='respuesta')
router.register(r'evaluaciones/episodios', EpisodioCefaleaViewSet, basename='episodio-cefalea')
urlpatterns = [
    path('', include(router.urls)),
]
