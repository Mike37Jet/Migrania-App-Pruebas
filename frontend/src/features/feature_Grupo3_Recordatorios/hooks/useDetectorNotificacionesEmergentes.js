import { useState, useEffect, useRef } from 'react';
import NotificacionesService from '../services/notificacionesService';

const useDetectorNotificacionesEmergentes = () => {
  const [alertaActual, setAlertaActual] = useState(null);
  const [recordatorioActual, setRecordatorioActual] = useState(null);
  const [mostrarAlerta, setMostrarAlerta] = useState(false);
  const [mostrarRecordatorio, setMostrarRecordatorio] = useState(false);
  
  // Referencias para evitar duplicados
  const alertasProcessadasRef = useRef(new Set());
  const recordatoriosProcessadosRef = useRef(new Set());
  const intervalosActivosRef = useRef(new Map());
  
  // Función para procesar automáticamente las notificaciones (reenvíos)
  const procesarNotificacionesAutomaticamente = async () => {
    try {
      console.log('🔧 Obteniendo tratamientos activos para procesamiento...');
      const tratamientosActivos = await NotificacionesService.obtenerTratamientosActivos();
      
      if (!tratamientosActivos || tratamientosActivos.length === 0) {
        console.log('⚠️ No hay tratamientos activos para procesar');
        return;
      }

      console.log(`🎯 Procesando ${tratamientosActivos.length} tratamientos activos...`);
      
      for (const tratamiento of tratamientosActivos) {
        try {
          console.log(`🔄 Procesando notificaciones para tratamiento ID: ${tratamiento.id}`);
          
          // Primer intento: procesar notificaciones existentes
          const resultado = await NotificacionesService.procesarNotificaciones(tratamiento.id);
          console.log(`✅ Tratamiento ${tratamiento.id} procesado:`, resultado);
          
          // Si no se procesaron notificaciones, intentar generar nuevas
          if (resultado.procesadas === 0) {
            try {
              console.log(`🏭 No hay notificaciones para procesar, intentando generar automáticamente...`);
              const generadas = await NotificacionesService.generarNotificacionesAutomaticas(tratamiento.id);
              console.log(`🎉 Notificaciones generadas para tratamiento ${tratamiento.id}:`, generadas);
              
              // Procesar las notificaciones recién generadas
              const resultadoFinal = await NotificacionesService.procesarNotificaciones(tratamiento.id);
              console.log(`✅ Notificaciones recién generadas procesadas:`, resultadoFinal);
            } catch (generarError) {
              console.warn(`⚠️ No se pudieron generar notificaciones automáticas para tratamiento ${tratamiento.id}:`, generarError.message);
            }
          }
          
        } catch (error) {
          console.error(`❌ Error procesando tratamiento ${tratamiento.id}:`, error);
          // Continuar con el siguiente tratamiento
        }
      }
      
      console.log('🎉 Procesamiento automático completado');
    } catch (error) {
      console.error('💥 Error fatal en procesamiento automático:', error);
      throw error; // Re-lanzar para que se maneje en el nivel superior
    }
  };

  // Función para obtener notificaciones pendientes
  const obtenerNotificaciones = async () => {
    try {
      const tratamientosActivos = await NotificacionesService.obtenerTratamientosActivos();
      
      if (!tratamientosActivos || tratamientosActivos.length === 0) {
        return { alertas: [], recordatorios: [] };
      }

      let todasLasAlertas = [];
      let todosLosRecordatorios = [];

      // REHABILITANDO: Procesar notificaciones automáticamente antes de obtenerlas
      console.log('🔄 Iniciando procesamiento automático de notificaciones...');
      try {
        await procesarNotificacionesAutomaticamente();
        console.log('✅ Procesamiento automático completado exitosamente');
      } catch (error) {
        console.error('❌ Error en procesamiento automático:', error);
        console.log('📝 Detalles del error:', {
          message: error.message,
          stack: error.stack,
          type: error.constructor.name
        });
        console.log('⏸️ Continuando sin procesamiento automático...');
      }

      for (const tratamiento of tratamientosActivos) {
        try {
          console.log(`🔍 Buscando notificaciones para tratamiento ID: ${tratamiento.id}`);
          const notificaciones = await NotificacionesService.obtenerNotificacionesPendientes(tratamiento.id);
          console.log(`📥 Notificaciones encontradas para tratamiento ${tratamiento.id}:`, notificaciones);
          
          if (notificaciones && notificaciones.alertas) {
            console.log(`🚨 Alertas encontradas: ${notificaciones.alertas.length}`);
            // Log detallado de cada alerta
            notificaciones.alertas.forEach((alerta, index) => {
              console.log(`🚨 Alerta ${index + 1}:`, {
                id: alerta.id,
                estado: alerta.estado,
                fecha_hora: alerta.fecha_hora,
                tipo: alerta.tipo || 'N/A'
              });
            });
            todasLasAlertas = [...todasLasAlertas, ...notificaciones.alertas];
          }
          
          if (notificaciones && notificaciones.recordatorios) {
            console.log(`📝 Recordatorios encontrados: ${notificaciones.recordatorios.length}`);
            // Log detallado de cada recordatorio
            notificaciones.recordatorios.forEach((recordatorio, index) => {
              console.log(`📝 Recordatorio ${index + 1}:`, {
                id: recordatorio.id,
                estado: recordatorio.estado,
                fecha_hora: recordatorio.fecha_hora,
                tipo: recordatorio.tipo || 'N/A'
              });
            });
            todosLosRecordatorios = [...todosLosRecordatorios, ...notificaciones.recordatorios];
          }
        } catch (error) {
          console.warn(`Error obteniendo notificaciones para tratamiento ${tratamiento.id}:`, error);
        }
      }

      console.log(`📊 RESUMEN FINAL - Alertas: ${todasLasAlertas.length}, Recordatorios: ${todosLosRecordatorios.length}`);
      
      // Log adicional para debugging
      console.log(`🔍 DETALLE DE NOTIFICACIONES FINALES:`);
      todasLasAlertas.forEach((alerta, index) => {
        console.log(`  🚨 Alerta ${index + 1}: ID=${alerta.id}, estado='${alerta.estado}'`);
      });
      todosLosRecordatorios.forEach((recordatorio, index) => {
        console.log(`  📝 Recordatorio ${index + 1}: ID=${recordatorio.id}, estado='${recordatorio.estado}'`);
      });

      return {
        alertas: todasLasAlertas,
        recordatorios: todosLosRecordatorios
      };

    } catch (error) {
      console.error('Error obteniendo notificaciones:', error);
      return { alertas: [], recordatorios: [] };
    }
  };

  // Función para mostrar una alerta
  const mostrarAlertaPopup = async (alerta) => {
    console.log(`🎯 INTENTANDO MOSTRAR ALERTA POPUP:`, alerta);
    const alertaKey = `alerta_${alerta.id}_${alerta.fecha_hora}`;
    console.log(`🔑 Clave de alerta: ${alertaKey}`);
    
    if (alertasProcessadasRef.current.has(alertaKey)) {
      console.log(`⚠️ Alerta ya procesada, saltando: ${alertaKey}`);
      return;
    }

    console.log(`✅ Alerta nueva, procesando: ${alertaKey}`);
    alertasProcessadasRef.current.add(alertaKey);
    
    setAlertaActual(alerta);
    setMostrarAlerta(true);
    console.log(`🚨 POPUP DE ALERTA ACTIVADO - mostrarAlerta=true`);

    // Auto-ocultar después de 1 minuto (60000ms)
    const timeoutId = setTimeout(() => {
      if (alertaActual && alertaActual.id === alerta.id) {
        handleCancelarAlerta(alerta);
      }
    }, 60000);

    intervalosActivosRef.current.set(alertaKey, timeoutId);
  };

  // Función para mostrar un recordatorio
  const mostrarRecordatorioPopup = async (recordatorio) => {
    console.log(`🎯 INTENTANDO MOSTRAR RECORDATORIO POPUP:`, recordatorio);
    const recordatorioKey = `recordatorio_${recordatorio.id}_${recordatorio.fecha_hora}`;
    console.log(`🔑 Clave de recordatorio: ${recordatorioKey}`);
    
    if (recordatoriosProcessadosRef.current.has(recordatorioKey)) {
      console.log(`⚠️ Recordatorio ya procesado, saltando: ${recordatorioKey}`);
      return;
    }

    console.log(`✅ Recordatorio nuevo, procesando: ${recordatorioKey}`);
    recordatoriosProcessadosRef.current.add(recordatorioKey);
    
    setRecordatorioActual(recordatorio);
    setMostrarRecordatorio(true);
    console.log(`📝 POPUP DE RECORDATORIO ACTIVADO - mostrarRecordatorio=true`);

    // Auto-ocultar después de 1 minuto (60000ms)
    const timeoutId = setTimeout(() => {
      if (recordatorioActual && recordatorioActual.id === recordatorio.id) {
        handleDesactivarRecordatorio(recordatorio);
      }
    }, 60000);

    intervalosActivosRef.current.set(recordatorioKey, timeoutId);
  };

  // Manejadores de eventos
  const handleConfirmarAlerta = async (alerta = null, estadoConfirmacion = 'tomado') => {
    try {
      // Usar la alerta pasada como parámetro o la que está en el estado
      const alertaAConfirmar = alerta || alertaActual;
      
      if (!alertaAConfirmar) {
        console.warn('No hay alerta para confirmar');
        return;
      }

      await NotificacionesService.confirmarAlerta(alertaAConfirmar.id, estadoConfirmacion);
      
      // Limpiar timeout si existe
      const alertaKey = `alerta_${alertaAConfirmar.id}_${alertaAConfirmar.fecha_hora}`;
      if (intervalosActivosRef.current.has(alertaKey)) {
        clearTimeout(intervalosActivosRef.current.get(alertaKey));
        intervalosActivosRef.current.delete(alertaKey);
      }
      
      setMostrarAlerta(false);
      setAlertaActual(null);
    } catch (error) {
      console.error('Error confirmando alerta:', error);
    }
  };

  const handleCancelarAlerta = async (alerta = null) => {
    try {
      // Usar la alerta pasada como parámetro o la que está en el estado
      const alertaACancelar = alerta || alertaActual;
      
      if (!alertaACancelar) {
        console.warn('No hay alerta para cancelar');
        return;
      }

      // Marcar como "no_tomado" cuando se cancela o se auto-oculta
      await NotificacionesService.confirmarAlertaNoTomada(alertaACancelar.id);
      
      // Limpiar timeout si existe
      const alertaKey = `alerta_${alertaACancelar.id}_${alertaACancelar.fecha_hora}`;
      if (intervalosActivosRef.current.has(alertaKey)) {
        clearTimeout(intervalosActivosRef.current.get(alertaKey));
        intervalosActivosRef.current.delete(alertaKey);
      }
      
      setMostrarAlerta(false);
      setAlertaActual(null);
    } catch (error) {
      console.error('Error cancelando alerta:', error);
    }
  };

  const handleDesactivarRecordatorio = async (recordatorio = null) => {
    try {
      // Usar el recordatorio pasado como parámetro o el que está en el estado
      const recordatorioADesactivar = recordatorio || recordatorioActual;
      
      if (!recordatorioADesactivar) {
        console.warn('No hay recordatorio para desactivar');
        return;
      }

      await NotificacionesService.desactivarRecordatorio(recordatorioADesactivar.id);
      
      // Limpiar timeout si existe
      const recordatorioKey = `recordatorio_${recordatorioADesactivar.id}_${recordatorioADesactivar.fecha_hora}`;
      if (intervalosActivosRef.current.has(recordatorioKey)) {
        clearTimeout(intervalosActivosRef.current.get(recordatorioKey));
        intervalosActivosRef.current.delete(recordatorioKey);
      }
      
      setMostrarRecordatorio(false);
      setRecordatorioActual(null);
    } catch (error) {
      console.error('Error desactivando recordatorio:', error);
    }
  };

  // Función principal para verificar notificaciones
  const verificarNotificaciones = async () => {
    console.log(`🚀 INICIANDO VERIFICACIÓN DE NOTIFICACIONES...`);
    try {
      const { alertas, recordatorios } = await obtenerNotificaciones();

      console.log(`🎯 VERIFICANDO NOTIFICACIONES - Alertas: ${alertas.length}, Recordatorios: ${recordatorios.length}`);

      // Procesar recordatorios primero
      for (const recordatorio of recordatorios) {
        console.log(`📝 Evaluando recordatorio ID ${recordatorio.id}, estado: ${recordatorio.estado}`);
        if (recordatorio.estado === 'activo' || recordatorio.estado === 'ACTIVO') {
          console.log(`✅ Mostrando recordatorio ID ${recordatorio.id}`);
          await mostrarRecordatorioPopup(recordatorio);
        } else {
          console.log(`⏭️ Recordatorio ID ${recordatorio.id} omitido por estado: ${recordatorio.estado}`);
        }
      }

      // Procesar alertas
      for (const alerta of alertas) {
        console.log(`🚨 Evaluando alerta ID ${alerta.id}, estado: ${alerta.estado}`);
        if (['SIN_CONFIRMAR', 'CONFIRMADO_TARDE', 'CONFIRMADO_MUY_TARDE', 'activo', 'sin_confirmar', 'confirmado_tarde', 'confirmado_muy_tarde'].includes(alerta.estado)) {
          console.log(`✅ Mostrando alerta ID ${alerta.id}`);
          await mostrarAlertaPopup(alerta);
        } else {
          console.log(`⏭️ Alerta ID ${alerta.id} omitida por estado: ${alerta.estado}`);
        }
      }

      console.log(`✅ VERIFICACIÓN COMPLETADA - Procesamiento terminado`);

    } catch (error) {
      console.error('Error verificando notificaciones:', error);
    }
  };

  // Efecto principal para el polling
  useEffect(() => {
    // Verificar inmediatamente al montar
    verificarNotificaciones();

    // Configurar polling cada 30 segundos
    const interval = setInterval(() => {
      verificarNotificaciones();
    }, 30000);

    // Cleanup
    return () => {
      clearInterval(interval);
      
      // Limpiar todos los timeouts activos
      intervalosActivosRef.current.forEach((timeoutId) => {
        clearTimeout(timeoutId);
      });
      intervalosActivosRef.current.clear();
      
      // Limpiar sets de procesados
      alertasProcessadasRef.current.clear();
      recordatoriosProcessadosRef.current.clear();
    };
  }, []);

  return {
    alertaActual,
    recordatorioActual,
    mostrarAlerta,
    mostrarRecordatorio,
    handleConfirmarAlerta,
    handleCancelarAlerta,
    handleDesactivarRecordatorio,
    verificarNotificaciones
  };
};

export default useDetectorNotificacionesEmergentes;
