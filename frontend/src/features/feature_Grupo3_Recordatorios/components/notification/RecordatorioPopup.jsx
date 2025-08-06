import React, { useState, useEffect } from 'react';
import { LightbulbFilamentIcon, InfoIcon, X } from '@phosphor-icons/react';
import styles from '../../styles/RecordatorioPopup.module.css';
import NotificacionesService from '../../services/notificacionesService';

const RecordatorioPopup = ({ 
  isOpen, 
  onClose,
  type,
  mensaje, // mensaje del recordatorio
  fecha_hora, // fecha_hora del recordatorio
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

  // Determinar tipo de recordatorio (medicamento o recomendación)
  let esMedicamento = false;
  if (type === 'medicina' || (mensaje && /toma|tomar|medic/i.test(mensaje))) {
    esMedicamento = true;
  }

  // Calcular minutos hasta la hora programada si es de medicamento
  let minutosRestantes = null;
  if (esMedicamento && fecha_hora) {
    try {
      const ahora = new Date();
      const fecha = new Date(fecha_hora);
      const diffMs = fecha - ahora;
      minutosRestantes = Math.round(diffMs / 60000);
    } catch (e) {
      minutosRestantes = null;
    }
  }

  // Icono y título según tipo
  const icono = esMedicamento
    ? <LightbulbFilamentIcon size={64} color="var(--secondary-light)" weight="fill" />
    : <InfoIcon size={64} color="var(--secondary-light)" weight="fill" />;
  const titulo = esMedicamento
    ? "Es hora de prepararte para tu medicación"
    : "Recuerda seguir las recomendaciones";

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
          {icono}
        </div>
        <div className={styles.content}>
          <h3 className={styles.title}>{titulo}</h3>
          <p className={styles.message}>
            {mensaje}
            {esMedicamento && typeof minutosRestantes === 'number' && minutosRestantes > 0 && (
              <span style={{ display: 'block', color: 'var(--color-secondary-dark)', fontWeight: 'bold', marginTop: 6 }}>
                dentro de {minutosRestantes} minuto{minutosRestantes === 1 ? '' : 's'}
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default RecordatorioPopup;