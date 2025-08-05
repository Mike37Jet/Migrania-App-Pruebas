import React, { useState } from 'react';
import { AlarmIcon } from '@phosphor-icons/react';
import styles from '../../styles/AlertaPopup.module.css';
import NotificacionesService from '../../services/notificacionesService';

const AlertaPopup = ({ 
  isOpen, 
  onConfirm, 
  onCancel, 
  title = "¿Tomaste la medicación?",
  message,
  confirmText = "SÍ",
  cancelText = "NO",
  alertaId = null
}) => {
  const [procesando, setProcesando] = useState(false);

  const handleConfirm = async () => {
    if (alertaId) {
      try {
        setProcesando(true);
        await NotificacionesService.confirmarAlerta(alertaId);
        console.log('Alerta confirmada exitosamente');
      } catch (error) {
        console.error('Error confirmando alerta:', error);
      } finally {
        setProcesando(false);
      }
    }
    
    if (onConfirm) {
      onConfirm();
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };
  if (!isOpen) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.popup}>
        <div className={styles.iconContainer}>
          <AlarmIcon size={64} color="var(--secondary-light)" weight="fill" />
        </div>
        
        <div className={styles.content}>
          <h3 className={styles.title}>{title}</h3>
          <p className={styles.message}>{message}</p>
        </div>
        
        <div className={styles.buttonContainer}>
          <button 
            className={styles.confirmBtn}
            onClick={handleConfirm}
            disabled={procesando}
          >
            {procesando ? 'Confirmando...' : confirmText}
          </button>
          
          <button 
            className={styles.cancelBtn}
            onClick={handleCancel}
            disabled={procesando}
          >
            {cancelText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AlertaPopup;