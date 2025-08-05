import React, { useState, useEffect } from 'react';
import { LightbulbFilamentIcon, InfoIcon, X } from '@phosphor-icons/react';
import styles from '../../styles/RecordatorioPopup.module.css';
import NotificacionesService from '../../services/notificacionesService';

const RecordatorioPopup = ({ 
  isOpen, 
  onClose,
  type,
  message,
  recordatorioId = null,
  modoSonido = "sonido"
}) => {
  const [procesando, setProcesando] = useState(false);

  const handleClose = async () => {
    if (onClose) {
      // Llamar directamente al handler del hook que se encarga de todo
      onClose();
    }
  };
  useEffect(() => {
    if (isOpen && modoSonido === "sonido") {
      // Sonido estándar (beep)
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(660, audioCtx.currentTime); // Frecuencia beep diferente
        oscillator.connect(audioCtx.destination);
        oscillator.start();
        setTimeout(() => {
          oscillator.stop();
          audioCtx.close();
        }, 200); // Duración del beep
      } catch (e) {
        if (typeof window !== 'undefined') {
          window.alert('¡Recordatorio!');
        }
      }
    }
  }, [isOpen, modoSonido]);
  if (!isOpen) return null;

  // Configuración según el tipo
  const getConfig = () => {
    switch (type) {
      case "recomendacion":
        return {
          title: "Recuerda seguir las recomendaciones",
          icon: <InfoIcon size={64} color="var(--secondary-light)" weight="fill" />
        };
      case "medicina":
      default:
        return {
          title: "Es hora de prepararte para tu medicación",
          icon: <LightbulbFilamentIcon size={64} color="var(--secondary-light)" weight="fill" />
        };
    }
  };

  const config = getConfig();

  return (
    <div className={styles.overlay}>
      <div className={styles.popup}>
        <button 
          className={styles.closeBtn}
          onClick={handleClose}
          title={procesando ? "Procesando..." : "Cerrar"}
          disabled={procesando}
        >
          <X size={24} color="var(--color-text)" weight="bold" />
        </button>
        
        <div>
          {config.icon}
        </div>
        
        <div className={styles.content}>
          <h3 className={styles.title}>{config.title}</h3>
          <p className={styles.message}>{message}</p>
        </div>
      </div>
    </div>
  );
};

export default RecordatorioPopup;