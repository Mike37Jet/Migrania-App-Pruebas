import React from 'react';
import { BellRingingIcon, BellSlashIcon, BellZIcon } from '@phosphor-icons/react';
import styles from '../../styles/BotonesDeConfiguracion.module.css';

const BotonesDeConfiguracion = ({ 
  onSonido, 
  onSilenciar, 
  onSuspender, 
  estadoActual = 'sonido' 
}) => {
  return (
    <div className={styles.botonesContainer}>
      <button 
        className={`${styles.boton} ${estadoActual === 'sonido' ? styles.activo : ''}`}
        onClick={onSonido}
        title="Activar sonido"
      >
        <BellRingingIcon size={24} />
        <span>Sonido</span>
      </button>
      
      <button 
        className={`${styles.boton} ${estadoActual === 'silencio' ? styles.activo : ''}`}
        onClick={onSilenciar}
        title="Silenciar"
      >
        <BellSlashIcon size={24} />
        <span>Silenciar</span>
      </button>
      
      <button 
        className={`${styles.boton} ${estadoActual === 'suspender' ? styles.activo : ''}`}
        onClick={onSuspender}
        title="Suspender"
      >
        <BellZIcon size={24} />
        <span>Suspender</span>
      </button>
    </div>
  );
};

export default BotonesDeConfiguracion;