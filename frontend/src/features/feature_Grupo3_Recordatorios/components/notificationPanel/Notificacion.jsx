import React from 'react';
import styles from '../../styles/Notificacion.module.css';

const Notificacion = ({ 
  tipo, 
  titulo, 
  mensaje, 
  tiempo, 
  icono 
}) => {
  return (
    <div className={`${styles.notificacion} ${styles[tipo]}`}>
      <div className={styles.iconoContainer}>
        {icono}
      </div>
      <div className={styles.contenido}>
        <h4 className={styles.titulo}>{titulo}</h4>
        <p className={styles.mensaje}>{mensaje}</p>
        <span className={styles.tiempo}>{tiempo}</span>
      </div>
    </div>
  );
};

export default Notificacion;