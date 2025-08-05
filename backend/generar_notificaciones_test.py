#!/usr/bin/env python
"""
Script para generar notificaciones reales de prueba ejecutando procesarNotificacionesPendientes()
Este script simula el comportamiento real del sistema de notificaciones de Django
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migraine_app.settings')
django.setup()

from tratamiento.models import Tratamiento, Medicamento, Alerta, Recordatorio, EstadoNotificacion
from usuarios.models import PacienteProfile
from evaluacion_diagnostico.models import EpisodioCefalea

def crear_tratamiento_prueba():
    """Crear un tratamiento de prueba con medicamentos y notificaciones"""
    print("🔧 Creando tratamiento de prueba...")
    
    # Buscar un paciente existente o crear uno de prueba
    try:
        paciente = PacienteProfile.objects.first()
        if not paciente:
            print("❌ No hay pacientes en la base de datos. Crea un paciente primero.")
            return None
    except Exception as e:
        print(f"❌ Error buscando paciente: {e}")
        return None

    # Buscar un episodio existente o crear uno de prueba
    try:
        episodio = EpisodioCefalea.objects.filter(paciente=paciente).first()
        if not episodio:
            print("❌ No hay episodios para este paciente. Crea un episodio primero.")
            return None
    except Exception as e:
        print(f"❌ Error buscando episodio: {e}")
        return None

    # Crear medicamento de prueba
    medicamento, created = Medicamento.objects.get_or_create(
        nombre="Ibuprofeno",
        defaults={
            'dosis': '400mg',
            'caracteristica': 'Antiinflamatorio',
            'hora_de_inicio': datetime.now().time(),
            'frecuencia_horas': 8,
            'duracion_dias': 3
        }
    )
    
    if created:
        print(f"✅ Medicamento creado: {medicamento}")
    else:
        print(f"📦 Medicamento existente: {medicamento}")

    # Crear tratamiento
    tratamiento, created = Tratamiento.objects.get_or_create(
        episodio=episodio,
        paciente=paciente,
        defaults={
            'fecha_inicio': timezone.now().date(),
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Tratamiento creado: {tratamiento}")
        tratamiento.medicamentos.add(medicamento)
        tratamiento.asignar_recomendaciones_generales()
        tratamiento.save()
    else:
        print(f"📦 Tratamiento existente: {tratamiento}")

    return tratamiento

def crear_notificaciones_inmediatas(tratamiento):
    """Crear notificaciones que deben activarse inmediatamente"""
    print("🔔 Creando notificaciones inmediatas...")
    
    ahora = timezone.now()
    
    # Crear alerta que debe mostrarse inmediatamente (estado ACTIVO -> SIN_CONFIRMAR)
    alerta_inmediata = Alerta.objects.create(
        mensaje="Es hora de tomar tu Ibuprofeno 400mg",
        fecha_hora=ahora - timedelta(minutes=1),  # Hace 1 minuto
        estado=EstadoNotificacion.ACTIVO,
        tratamiento=tratamiento,
        numero_alerta=1,
        duracion=15,  # 15 minutos
        tiempo_espera=15
    )
    print(f"✅ Alerta inmediata creada: {alerta_inmediata}")

    # Crear recordatorio que debe mostrarse inmediatamente
    recordatorio_inmediato = Recordatorio.objects.create(
        mensaje="Recordatorio: Mantén una rutina regular de sueño",
        fecha_hora=ahora - timedelta(minutes=2),  # Hace 2 minutos
        estado=EstadoNotificacion.ACTIVO,
        tratamiento=tratamiento
    )
    print(f"✅ Recordatorio inmediato creado: {recordatorio_inmediato}")

    return alerta_inmediata, recordatorio_inmediato

def procesar_notificaciones(tratamiento):
    """Ejecutar procesarNotificacionesPendientes para generar estados SIN_CONFIRMAR"""
    print("⚡ Ejecutando procesarNotificacionesPendientes...")
    
    # Ejecutar el procesamiento de notificaciones
    notificaciones_procesadas = tratamiento.procesarNotificacionesPendientes()
    
    print(f"✅ Procesadas {len(notificaciones_procesadas)} notificaciones")
    
    for notif in notificaciones_procesadas:
        print(f"   📨 {type(notif).__name__}: {notif.mensaje} - Estado: {notif.estado}")
    
    return notificaciones_procesadas

def mostrar_estado_notificaciones(tratamiento):
    """Mostrar el estado actual de las notificaciones"""
    print("\n📊 ESTADO ACTUAL DE LAS NOTIFICACIONES:")
    print("="*50)
    
    # Alertas
    alertas = tratamiento.alertas.all()
    print(f"🚨 ALERTAS ({alertas.count()}):")
    for alerta in alertas:
        print(f"   ID: {alerta.id} | Estado: {alerta.estado} | Mensaje: {alerta.mensaje}")
        print(f"   Fecha/Hora: {alerta.fecha_hora} | Duración: {alerta.duracion}min")
        print()
    
    # Recordatorios
    recordatorios = tratamiento.recordatorios.all()
    print(f"📋 RECORDATORIOS ({recordatorios.count()}):")
    for recordatorio in recordatorios:
        print(f"   ID: {recordatorio.id} | Estado: {recordatorio.estado} | Mensaje: {recordatorio.mensaje}")
        print(f"   Fecha/Hora: {recordatorio.fecha_hora}")
        print()
    
    # Notificaciones pendientes usando el método del modelo
    notificaciones_pendientes = tratamiento.obtenerNotificacionesPendientes()
    print(f"⏰ NOTIFICACIONES PENDIENTES ({len(notificaciones_pendientes)}):")
    for notif in notificaciones_pendientes:
        print(f"   {type(notif).__name__}: {notif.estado} - {notif.mensaje}")

def main():
    print("🚀 GENERADOR DE NOTIFICACIONES REALES PARA TESTING")
    print("="*60)
    
    try:
        # Paso 1: Crear tratamiento de prueba
        tratamiento = crear_tratamiento_prueba()
        if not tratamiento:
            print("❌ No se pudo crear el tratamiento. Saliendo...")
            return
        
        print(f"\n📋 Trabajando con tratamiento ID: {tratamiento.id}")
        
        # Paso 2: Crear notificaciones inmediatas
        alerta, recordatorio = crear_notificaciones_inmediatas(tratamiento)
        
        # Paso 3: Procesar notificaciones para cambiar estados
        notificaciones_procesadas = procesar_notificaciones(tratamiento)
        
        # Paso 4: Mostrar estado final
        mostrar_estado_notificaciones(tratamiento)
        
        print("\n🎯 INSTRUCCIONES PARA FRONTEND:")
        print("="*40)
        print(f"1. Usa el tratamientoId: {tratamiento.id}")
        print("2. Llama al endpoint: GET /api/tratamientos/{tratamiento.id}/notificaciones-pendientes/")
        print("3. Deberías ver alertas con estado 'sin_confirmar' y recordatorios con estado 'activo'")
        print("4. Los popups deberían aparecer automáticamente en el frontend")
        
        print("\n✅ Script completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error ejecutando el script: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
