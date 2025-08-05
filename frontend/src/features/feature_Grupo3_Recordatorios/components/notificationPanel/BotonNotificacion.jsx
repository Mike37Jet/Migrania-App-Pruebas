import React from 'react';
import { BellIcon } from '@phosphor-icons/react';
import styles from '../../styles/BotonNotificacion.module.css';

const BotonNotificacion = ({ onClick, size = 32, className = '', hasNotifications = false, notificationCount = 0 }) => {
  return (
    <button 
      onClick={onClick}
      className={`${styles.notificationBtn} ${className}`}
      title="Ver notificaciones"
    >
      <div className={styles.iconContainer}>
        <BellIcon
          size={size}
          color="var(--color-background)"
          weight="fill"
          style={{
            stroke: "var(--color-text)",
            strokeWidth: '13px'
          }}
        />
        
        {hasNotifications && (
          <span className={styles.badge}>
            {notificationCount > 0 && notificationCount < 100 ? notificationCount : notificationCount >= 100 ? '99+' : ''}
          </span>
        )}
      </div>
    </button>
  );
};

export default BotonNotificacion;