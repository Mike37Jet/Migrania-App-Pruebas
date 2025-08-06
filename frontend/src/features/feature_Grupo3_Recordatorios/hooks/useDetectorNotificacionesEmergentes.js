import { useState, useEffect, useRef } from 'react';
import NotificacionesService from '../services/notificacionesService';

const useDetectorNotificacionesEmergentes = () => {
  const [alertaActual, setAlertaActual] = useState(null);
  const [recordatorioActual, setRecordatorioActual] = useState(null);
  const [mostrarAlerta, setMostrarAlerta] = useState(false);
  const [mostrarRecordatorio, setMostrarRecordatorio] = useState(false);
  // Array de notificaciones mostradas (solo frontend)
  const [notificacionesMostradas, setNotificacionesMostradas] = useState([]);
  
  // Referencias para evitar duplicados
  const alertasProcessadasRef = useRef(new Set());
  const recordatoriosProcessadosRef = useRef(new Set());
  const intervalosActivosRef = useRef(new Map());
  
  // Ya no se procesan notificaciones automáticamente en el frontend.
  // El frontend solo consulta las alertas y recordatorios pendientes por paciente y decide mostrar popups según la hora programada.

  // Función para obtener alertas y recordatorios pendientes por paciente
  // El frontend debe filtrar por hora programada (fecha_hora) para decidir si mostrar popup
  const obtenerNotificaciones = async () => {
    try {
      const pacienteId = await NotificacionesService.obtenerPacienteId();
      if (!pacienteId) {
        console.warn('No se pudo obtener pacienteId, omitiendo consulta de notificaciones');
        return { alertas: [], recordatorios: [] };
      }
      // Llamar a los endpoints nuevos por paciente
      const [alertas, recordatorios] = await Promise.all([
        NotificacionesService.obtenerAlertasPorPaciente(pacienteId),
        NotificacionesService.obtenerRecordatoriosPorPaciente(pacienteId)
      ]);
      return { alertas, recordatorios };
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

    // Agregar alerta a notificaciones mostradas (si no existe ya)
    setNotificacionesMostradas(prev => {
      const existe = prev.some(n => n.id === alerta.id && n.fecha_hora === alerta.fecha_hora);
      if (!existe) {
        return [...prev, { ...alerta, tipo: alerta.tipo || 'alerta' }];
      }
      return prev;
    });

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

    // Agregar recordatorio a notificaciones mostradas (si no existe ya)
    setNotificacionesMostradas(prev => {
      const existe = prev.some(n => n.id === recordatorio.id && n.fecha_hora === recordatorio.fecha_hora);
      if (!existe) {
        return [...prev, { ...recordatorio, tipo: recordatorio.tipo || 'recordatorio' }];
      }
      return prev;
    });

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
        if ((recordatorio.estado === 'activo' || recordatorio.estado === 'ACTIVO') && recordatorio.fecha_hora) {
          // Comparar usando hora local del usuario
          const ahoraLocal = new Date();
          const fechaRecordatorioLocal = new Date(recordatorio.fecha_hora);
          console.log(`⏰ [RECORDATORIO] Comparando hora LOCAL: fechaRecordatorio=${fechaRecordatorioLocal.toLocaleString()} <= ahora=${ahoraLocal.toLocaleString()} ?`, fechaRecordatorioLocal <= ahoraLocal);
          if (fechaRecordatorioLocal <= ahoraLocal) {
            // Mostrar popup solo si está en la hora, pero siempre guardar en la lista del modal
            setNotificacionesMostradas(prev => {
              const existe = prev.some(n => n.id === recordatorio.id && n.fecha_hora === recordatorio.fecha_hora);
              if (!existe) {
                return [...prev, { ...recordatorio, tipo: recordatorio.tipo || 'recordatorio' }];
              }
              return prev;
            });
            console.log(`✅ Mostrando recordatorio ID ${recordatorio.id}`);
            await mostrarRecordatorioPopup(recordatorio);
          } else {
            // Si la fecha ya pasó pero no está activa, igual guardar en la lista del modal
            const ahoraLocal = new Date();
            console.log(`⏰ [RECORDATORIO] Comparando hora LOCAL (no activo): fechaRecordatorio=${fechaRecordatorioLocal.toLocaleString()} < ahora=${ahoraLocal.toLocaleString()} ?`, fechaRecordatorioLocal < ahoraLocal);
            if (fechaRecordatorioLocal < ahoraLocal) {
              setNotificacionesMostradas(prev => {
                const existe = prev.some(n => n.id === recordatorio.id && n.fecha_hora === recordatorio.fecha_hora);
                if (!existe) {
                  return [...prev, { ...recordatorio, tipo: recordatorio.tipo || 'recordatorio' }];
                }
                return prev;
              });
            }
            console.log(`⏭️ Recordatorio ID ${recordatorio.id} omitido por hora futura: ${recordatorio.fecha_hora}`);
          }
        } else {
          // Si la fecha ya pasó pero el estado no es activo, igual guardar en la lista del modal
          if (recordatorio.fecha_hora) {
            const ahoraLocal = new Date();
            const fechaRecordatorioLocal = new Date(recordatorio.fecha_hora);
            console.log(`⏰ [RECORDATORIO] Comparando hora LOCAL (no activo, else): fechaRecordatorio=${fechaRecordatorioLocal.toLocaleString()} < ahora=${ahoraLocal.toLocaleString()} ?`, fechaRecordatorioLocal < ahoraLocal);
            if (fechaRecordatorioLocal < ahoraLocal) {
              setNotificacionesMostradas(prev => {
                const existe = prev.some(n => n.id === recordatorio.id && n.fecha_hora === recordatorio.fecha_hora);
                if (!existe) {
                  return [...prev, { ...recordatorio, tipo: recordatorio.tipo || 'recordatorio' }];
                }
                return prev;
              });
            }
          }
          console.log(`⏭️ Recordatorio ID ${recordatorio.id} omitido por estado: ${recordatorio.estado}`);
        }
      }

      // Procesar alertas
      for (const alerta of alertas) {
        console.log(`🚨 Evaluando alerta ID ${alerta.id}, estado: ${alerta.estado}`);
        if ((['SIN_CONFIRMAR', 'CONFIRMADO_TARDE', 'CONFIRMADO_MUY_TARDE', 'activo', 'sin_confirmar', 'confirmado_tarde', 'confirmado_muy_tarde'].includes(alerta.estado)) && alerta.fecha_hora) {
          // Comparar usando hora local del usuario
          const ahoraLocal = new Date();
          const fechaAlertaLocal = new Date(alerta.fecha_hora);
          console.log(`⏰ [ALERTA] Comparando hora LOCAL: fechaAlerta=${fechaAlertaLocal.toLocaleString()} <= ahora=${ahoraLocal.toLocaleString()} ?`, fechaAlertaLocal <= ahoraLocal);
          if (fechaAlertaLocal <= ahoraLocal) {
            setNotificacionesMostradas(prev => {
              const existe = prev.some(n => n.id === alerta.id && n.fecha_hora === alerta.fecha_hora);
              if (!existe) {
                return [...prev, { ...alerta, tipo: alerta.tipo || 'alerta' }];
              }
              return prev;
            });
            console.log(`✅ Mostrando alerta ID ${alerta.id}`);
            await mostrarAlertaPopup(alerta);
          } else {
            // Si la fecha ya pasó pero no está activa, igual guardar en la lista del modal
            const ahoraLocal = new Date();
            console.log(`⏰ [ALERTA] Comparando hora LOCAL (no activa): fechaAlerta=${fechaAlertaLocal.toLocaleString()} < ahora=${ahoraLocal.toLocaleString()} ?`, fechaAlertaLocal < ahoraLocal);
            if (fechaAlertaLocal < ahoraLocal) {
              setNotificacionesMostradas(prev => {
                const existe = prev.some(n => n.id === alerta.id && n.fecha_hora === alerta.fecha_hora);
                if (!existe) {
                  return [...prev, { ...alerta, tipo: alerta.tipo || 'alerta' }];
                }
                return prev;
              });
            }
            console.log(`⏭️ Alerta ID ${alerta.id} omitida por hora futura: ${alerta.fecha_hora}`);
          }
        } else {
          // Si la fecha ya pasó pero el estado no es válido, igual guardar en la lista del modal
          if (alerta.fecha_hora) {
            const ahoraLocal = new Date();
            const fechaAlertaLocal = new Date(alerta.fecha_hora);
            console.log(`⏰ [ALERTA] Comparando hora LOCAL (no activa, else): fechaAlerta=${fechaAlertaLocal.toLocaleString()} < ahora=${ahoraLocal.toLocaleString()} ?`, fechaAlertaLocal < ahoraLocal);
            if (fechaAlertaLocal < ahoraLocal) {
              setNotificacionesMostradas(prev => {
                const existe = prev.some(n => n.id === alerta.id && n.fecha_hora === alerta.fecha_hora);
                if (!existe) {
                  return [...prev, { ...alerta, tipo: alerta.tipo || 'alerta' }];
                }
                return prev;
              });
            }
          }
          console.log(`⏭️ Alerta ID ${alerta.id} omitida por estado: ${alerta.estado}`);
        }
      }

      console.log(`✅ VERIFICACIÓN COMPLETADA - Procesamiento terminado`);

    } catch (error) {
      console.error('Error verificando notificaciones:', error);
    }
  };

  // Efecto principal para el polling
  // El pacienteId debe ser proporcionado por el contexto de usuario autenticado
  useEffect(() => {
    const pacienteId = /* obtener pacienteId del contexto de usuario autenticado */ null;
    if (!pacienteId) return;

    // Verificar inmediatamente al montar
    verificarNotificaciones(pacienteId);

    // Configurar polling cada 30 segundos
    const interval = setInterval(() => {
      verificarNotificaciones(pacienteId);
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

  // Permite limpiar el array de notificaciones mostradas (para el modal)
  const limpiarNotificacionesMostradas = () => setNotificacionesMostradas([]);

  return {
    alertaActual,
    recordatorioActual,
    mostrarAlerta,
    mostrarRecordatorio,
    handleConfirmarAlerta,
    handleCancelarAlerta,
    handleDesactivarRecordatorio,
    verificarNotificaciones,
    notificacionesMostradas,
    limpiarNotificacionesMostradas,
    // Documentación: ahora el frontend decide mostrar popups según la hora programada de cada alerta/recordatorio
    // usando los endpoints /api/tratamientos/alertas-por-paciente/{paciente_id}/ y /api/tratamientos/recordatorios-por-paciente/{paciente_id}/
  };
};

export default useDetectorNotificacionesEmergentes;
