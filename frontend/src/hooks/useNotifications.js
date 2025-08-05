// useNotifications.js - Hook personalizado para manejar notificaciones

import { useState, useEffect, useCallback } from 'react';
import NotificationService from '../services/NotificationService';

export const useNotifications = (tratamientoId) => {
  const [notificationService] = useState(new NotificationService());
  const [notificaciones, setNotificaciones] = useState({ alertas: [], recordatorios: [], total: 0 });
  const [loading, setLoading] = useState(false);

  const cargarNotificaciones = useCallback(async () => {
    setLoading(true);
    try {
      const data = await notificationService.obtenerNotificacionesPendientes(tratamientoId);
      setNotificaciones(data);
    } catch (error) {
      console.error('Error al cargar notificaciones:', error);
    } finally {
      setLoading(false);
    }
  }, [notificationService, tratamientoId]);

  const confirmarAlerta = async (alertaId, estado, hora = null) => {
    try {
      await notificationService.cambiarEstadoAlerta(alertaId, estado, hora);
      await cargarNotificaciones(); // Recargar notificaciones
    } catch (error) {
      console.error('Error al confirmar alerta:', error);
      throw error;
    }
  };

  const desactivarRecordatorio = async (recordatorioId) => {
    try {
      await notificationService.desactivarRecordatorio(recordatorioId);
      await cargarNotificaciones(); // Recargar notificaciones
    } catch (error) {
      console.error('Error al desactivar recordatorio:', error);
      throw error;
    }
  };

  const mostrarRecordatorio = async (recordatorioId) => {
    try {
      return await notificationService.mostrarRecordatorio(recordatorioId);
    } catch (error) {
      console.error('Error al mostrar recordatorio:', error);
      throw error;
    }
  };

  useEffect(() => {
    if (tratamientoId) {
      cargarNotificaciones();
    }
  }, [tratamientoId, cargarNotificaciones]);

  return {
    notificaciones,
    loading,
    cargarNotificaciones,
    confirmarAlerta,
    desactivarRecordatorio,
    mostrarRecordatorio
  };
};
