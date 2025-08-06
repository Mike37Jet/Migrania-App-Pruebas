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
    const alertaKey = `alerta_${alerta.id}_${alerta.fecha_hora}`;
    if (alertasProcessadasRef.current.has(alertaKey)) {
      return;
    }
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
    // ...

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
    const recordatorioKey = `recordatorio_${recordatorio.id}_${recordatorio.fecha_hora}`;
    if (recordatoriosProcessadosRef.current.has(recordatorioKey)) {
      return;
    }
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
    // ...

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
      // Solo ocultar el popup, NO eliminar del array de notificacionesMostradas
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
      // Solo ocultar el popup, NO eliminar del array de notificacionesMostradas
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
      // Solo ocultar el popup, NO eliminar del array de notificacionesMostradas
      setMostrarRecordatorio(false);
      setRecordatorioActual(null);
    } catch (error) {
      console.error('Error desactivando recordatorio:', error);
    }
  };

  // Función principal para verificar notificaciones
  const verificarNotificaciones = async () => {
    console.log('[Notificaciones] Revisando notificaciones pendientes...');
    try {
      const { alertas, recordatorios } = await obtenerNotificaciones();

      // ...

      // Procesar recordatorios primero
      for (const recordatorio of recordatorios) {
        // ...
        if ((recordatorio.estado === 'activo' || recordatorio.estado === 'ACTIVO') && recordatorio.fecha_hora) {
          // Comparar usando hora local del usuario
          const ahoraLocal = new Date();
          const fechaRecordatorioLocal = new Date(recordatorio.fecha_hora);
          // ...
          if (fechaRecordatorioLocal <= ahoraLocal) {
            // Mostrar popup solo si está en la hora, pero siempre guardar en la lista del modal
            setNotificacionesMostradas(prev => {
              const existe = prev.some(n => n.id === recordatorio.id && n.fecha_hora === recordatorio.fecha_hora);
              if (!existe) {
                return [...prev, { ...recordatorio, tipo: recordatorio.tipo || 'recordatorio' }];
              }
              return prev;
            });
            // ...
            await mostrarRecordatorioPopup(recordatorio);
          } else {
            // Si la fecha ya pasó pero no está activa, igual guardar en la lista del modal
            const ahoraLocal = new Date();
            // ...
            if (fechaRecordatorioLocal < ahoraLocal) {
              setNotificacionesMostradas(prev => {
                const existe = prev.some(n => n.id === recordatorio.id && n.fecha_hora === recordatorio.fecha_hora);
                if (!existe) {
                  return [...prev, { ...recordatorio, tipo: recordatorio.tipo || 'recordatorio' }];
                }
                return prev;
              });
            }
            // ...
          }
        } else {
          // Si la fecha ya pasó pero el estado no es activo, igual guardar en la lista del modal
          if (recordatorio.fecha_hora) {
            const ahoraLocal = new Date();
            const fechaRecordatorioLocal = new Date(recordatorio.fecha_hora);
          // ...
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
            // ...
        }
      }

      // Procesar alertas
      for (const alerta of alertas) {
        // ...
        if ((['SIN_CONFIRMAR', 'CONFIRMADO_TARDE', 'CONFIRMADO_MUY_TARDE', 'activo', 'sin_confirmar', 'confirmado_tarde', 'confirmado_muy_tarde'].includes(alerta.estado)) && alerta.fecha_hora) {
          // Comparar usando hora local del usuario
          const ahoraLocal = new Date();
          const fechaAlertaLocal = new Date(alerta.fecha_hora);
          // ...
          if (fechaAlertaLocal <= ahoraLocal) {
            setNotificacionesMostradas(prev => {
              const existe = prev.some(n => n.id === alerta.id && n.fecha_hora === alerta.fecha_hora);
              if (!existe) {
                return [...prev, { ...alerta, tipo: alerta.tipo || 'alerta' }];
              }
              return prev;
            });
            // ...
            await mostrarAlertaPopup(alerta);
          } else {
            // Si la fecha ya pasó pero no está activa, igual guardar en la lista del modal
            const ahoraLocal = new Date();
            // ...
            if (fechaAlertaLocal < ahoraLocal) {
              setNotificacionesMostradas(prev => {
                const existe = prev.some(n => n.id === alerta.id && n.fecha_hora === alerta.fecha_hora);
                if (!existe) {
                  return [...prev, { ...alerta, tipo: alerta.tipo || 'alerta' }];
                }
                return prev;
              });
            }
            // ...
          }
        } else {
          // Si la fecha ya pasó pero el estado no es válido, igual guardar en la lista del modal
          if (alerta.fecha_hora) {
            const ahoraLocal = new Date();
            const fechaAlertaLocal = new Date(alerta.fecha_hora);
          // ...
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
            // ...
        }
      }

      // ...

    } catch (error) {
      console.error('Error verificando notificaciones:', error);
    }
  };

  // Efecto principal para el polling automático cada 1 minuto
  useEffect(() => {
    let interval = null;
    let cancelado = false;

    const iniciarPolling = async () => {
      const pacienteId = await NotificacionesService.obtenerPacienteId();
      if (!pacienteId) {
        console.warn('No se pudo obtener pacienteId para el polling automático');
        return;
      }
      // Verificar inmediatamente al montar
      if (!cancelado) await verificarNotificaciones();
      // Configurar polling cada 1 minuto
      interval = setInterval(() => {
        if (!cancelado) verificarNotificaciones();
      }, 60000);
    };

    iniciarPolling();

    // Cleanup
    return () => {
      cancelado = true;
      if (interval) clearInterval(interval);
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
