import React, { useState, useEffect, useCallback } from 'react';
import { AlarmIcon, LightbulbFilamentIcon, SirenIcon } from '@phosphor-icons/react';
import Notificacion from './Notificacion';
import ConfigurationButtons from './BotonesDeConfiguracion';
import styles from '../../styles/ModalNotificaciones.module.css';
import NotificacionesService from '../../services/notificacionesService';

const ModalNotificaciones = ({ isOpen, onClose, tratamientoId = 1, notificacionesExternas = null, onNotificacionesChange = null, modoSonido = "sonido", setModoSonido }) => {
  // El estado de sonido ahora viene del Dashboard
  const [notificaciones, setNotificaciones] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Función para obtener el icono según el tipo
  const obtenerIcono = (tipo) => {
    switch (tipo) {
      case 'medicacion':
        return <AlarmIcon size={32} color="#bad8ecff" weight="fill" />;
      case 'recordatorio':
        return <LightbulbFilamentIcon size={32} color="#f5e400ff" weight="fill" />;
      case 'alerta':
        return <SirenIcon size={32} color="#AA4D53" weight="fill" />;
      default:
        return <AlarmIcon size={32} color="#bad8ecff" weight="fill" />;
    }
  };

  // Cargar notificaciones cuando se abre el modal
  const cargarNotificaciones = useCallback(async () => {
    setCargando(true);
    setError(null);
    
    try {
      // Obtener datos de diferentes endpoints
      const [alertasData, recordatoriosData, notificacionesPendientes] = await Promise.allSettled([
        NotificacionesService.obtenerAlertas(tratamientoId),
        NotificacionesService.obtenerRecordatorios(tratamientoId),
        NotificacionesService.obtenerNotificacionesPendientes(tratamientoId)
      ]);

      const todasLasNotificaciones = [];

      // Procesar alertas
      if (alertasData.status === 'fulfilled' && alertasData.value) {
        const alertas = Array.isArray(alertasData.value) ? alertasData.value : [alertasData.value];
        alertas.forEach(alerta => {
          if (alerta.activa && !alerta.confirmada) {
            const notifFormateada = NotificacionesService.formatearNotificacion(alerta, 'alerta');
            notifFormateada.icono = obtenerIcono(notifFormateada.tipo);
            todasLasNotificaciones.push(notifFormateada);
          }
        });
      }

      // Procesar recordatorios
      if (recordatoriosData.status === 'fulfilled' && recordatoriosData.value) {
        const recordatorios = Array.isArray(recordatoriosData.value) ? recordatoriosData.value : [recordatoriosData.value];
        recordatorios.forEach(recordatorio => {
          if (recordatorio.activo) {
            const notifFormateada = NotificacionesService.formatearNotificacion(recordatorio, 'recordatorio');
            notifFormateada.icono = obtenerIcono(notifFormateada.tipo);
            todasLasNotificaciones.push(notifFormateada);
          }
        });
      }

      // Procesar notificaciones pendientes
      if (notificacionesPendientes.status === 'fulfilled' && notificacionesPendientes.value) {
        const pendientes = notificacionesPendientes.value;
        if (pendientes.alertas) {
          pendientes.alertas.forEach(alerta => {
            const notifFormateada = NotificacionesService.formatearNotificacion(alerta, 'alerta');
            notifFormateada.icono = obtenerIcono(notifFormateada.tipo);
            todasLasNotificaciones.push(notifFormateada);
          });
        }
        if (pendientes.recordatorios) {
          pendientes.recordatorios.forEach(recordatorio => {
            const notifFormateada = NotificacionesService.formatearNotificacion(recordatorio, 'recordatorio');
            notifFormateada.icono = obtenerIcono(notifFormateada.tipo);
            todasLasNotificaciones.push(notifFormateada);
          });
        }
      }

      // Si no hay notificaciones de la API, usar datos de fallback
      if (todasLasNotificaciones.length === 0) {
        setNotificaciones([
          {
            id: 'fallback-1',
            tipo: 'medicacion',
            titulo: 'Es hora de prepararte para tu medicación',
            mensaje: 'Toma tu medicamento según la prescripción médica',
            tiempo: 'Ahora',
            icono: obtenerIcono('medicacion')
          },
          {
            id: 'fallback-2',
            tipo: 'recordatorio',
            titulo: 'Recuerda:',
            mensaje: 'Mantén un estilo de vida saludable',
            tiempo: '1h',
            icono: obtenerIcono('recordatorio')
          }
        ]);
      } else {
        setNotificaciones(todasLasNotificaciones);
      }

    } catch (error) {
      console.error('Error cargando notificaciones:', error);
      setError('Error al cargar las notificaciones');
      
      // Mostrar notificaciones de fallback en caso de error
      setNotificaciones([
        {
          id: 'error-1',
          tipo: 'alerta',
          titulo: 'Error de conexión',
          mensaje: 'No se pudieron cargar las notificaciones',
          tiempo: 'Ahora',
          icono: obtenerIcono('alerta')
        }
      ]);
    } finally {
      setCargando(false);
    }
  }, [tratamientoId]);

  useEffect(() => {
    if (isOpen) {
      if (notificacionesExternas) {
        // Usar notificaciones que vienen del Dashboard
        setNotificaciones(notificacionesExternas);
        setCargando(false);
      } else if (tratamientoId) {
        // Cargar notificaciones si no vienen del Dashboard
        cargarNotificaciones();
      }
    }
  }, [isOpen, tratamientoId, cargarNotificaciones, notificacionesExternas]);

  const handleSonido = () => setModoSonido && setModoSonido('sonido');
  const handleSilenciar = () => setModoSonido && setModoSonido('silencio');
  const handleSuspender = () => setModoSonido && setModoSonido('suspender');

  const handleBorrarTodo = async () => {
    try {
      // Solo limpiar la lista visual del modal (frontend)
      setNotificaciones([]); // Limpiar la lista inmediatamente
      
      console.log('Lista de notificaciones del modal limpiada');
      
      // Opcionalmente, notificar al componente padre que se limpió la lista
      if (onNotificacionesChange) {
        onNotificacionesChange();
      }
      
    } catch (error) {
      console.error('Error limpiando lista de notificaciones:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.titulo}>Notificaciones</h2>
        </div>

        <ConfigurationButtons 
          onSonido={handleSonido}
          onSilenciar={handleSilenciar}
          onSuspender={handleSuspender}
          estadoActual={modoSonido}
        />

        <div className={styles.notificacionesList}>
          {cargando ? (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-text)' }}>
              Cargando notificaciones...
            </div>
          ) : error && notificaciones.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#e74c3c' }}>
              {error}
            </div>
          ) : notificaciones.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-text)' }}>
              No hay notificaciones pendientes
            </div>
          ) : (
            notificaciones.map(notificacion => (
              <Notificacion 
                key={notificacion.id}
                tipo={notificacion.tipo}
                titulo={notificacion.titulo}
                mensaje={notificacion.mensaje}
                tiempo={notificacion.tiempo}
                icono={notificacion.icono}
              />
            ))
          )}
        </div>

        <button className={styles.borrarTodoBtn} onClick={handleBorrarTodo}>
          Borrar todo
        </button>
      </div>
    </div>
  );
};

export default ModalNotificaciones;