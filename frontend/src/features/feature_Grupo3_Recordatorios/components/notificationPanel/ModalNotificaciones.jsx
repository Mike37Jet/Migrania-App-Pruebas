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
  // Ya no se consultan endpoints por tratamientoId. Si no hay notificacionesExternas, el modal queda vacío.
  const cargarNotificaciones = useCallback(() => {
    setCargando(false);
    setError(null);
    setNotificaciones([]);
  }, []);

  useEffect(() => {
    if (isOpen) {
      if (notificacionesExternas) {
        // Usar notificaciones que vienen del Dashboard
        setNotificaciones(notificacionesExternas);
        setCargando(false);
      } else {
        // Si no hay notificacionesExternas, el modal queda vacío
        cargarNotificaciones();
      }
    }
  }, [isOpen, cargarNotificaciones, notificacionesExternas]);

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