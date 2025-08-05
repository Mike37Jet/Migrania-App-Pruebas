import React, { useState, useEffect } from 'react';
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
  alertaId = null,
  modoSonido = "sonido",
  horaMedicacion = null // Nueva prop opcional
}) => {
  const [procesando, setProcesando] = useState(false);

  const handleConfirm = async () => {
    if (onConfirm) {
      // Llamar directamente al handler del hook que se encarga de todo
      onConfirm();
    }
  };

  const handleCancel = async () => {
    if (onCancel) {
      // Llamar directamente al handler del hook que se encarga de todo
      onCancel();
    }
  };
  useEffect(() => {
    if (isOpen && modoSonido === "sonido") {
      // Sonido estándar (beep)
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // Frecuencia beep
        oscillator.connect(audioCtx.destination);
        oscillator.start();
        setTimeout(() => {
          oscillator.stop();
          audioCtx.close();
        }, 200); // Duración del beep
      } catch (e) {
        // Fallback si el navegador no soporta AudioContext
        if (typeof window !== 'undefined') {
          window.alert('¡Alerta!');
        }
      }
    }
  }, [isOpen, modoSonido]);
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
          {horaMedicacion && (
            <div className={styles.horaMedicacion} style={{ marginTop: 8, color: "var(--color-secondary-dark)", fontWeight: "bold" }}>
              Hora de medicación: {horaMedicacion}
            </div>
          )}
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
            {procesando ? 'Procesando...' : cancelText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AlertaPopup;