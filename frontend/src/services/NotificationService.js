// NotificationService.js - Servicio para manejar las notificaciones

class NotificationService {
  constructor(baseURL = '/api/tratamientos') {
    this.baseURL = baseURL;
  }

  // Obtener la siguiente alerta de un tratamiento
  async obtenerSiguienteAlerta(tratamientoId) {
    try {
      const response = await fetch(`${this.baseURL}/${tratamientoId}/siguiente-alerta/`);
      
      if (response.status === 204) {
        return null; // No hay alertas pendientes
      }
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al obtener siguiente alerta:', error);
      throw error;
    }
  }

  // Cambiar estado de una alerta
  async cambiarEstadoAlerta(alertaId, nuevoEstado, horaConfirmacion = null) {
    try {
      const data = { nuevo_estado: nuevoEstado };
      if (horaConfirmacion) {
        data.hora_confirmacion = horaConfirmacion;
      }

      const response = await fetch(`${this.baseURL}/alerta/${alertaId}/estado/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error al cambiar estado de alerta:', error);
      throw error;
    }
  }

  // Mostrar un recordatorio
  async mostrarRecordatorio(recordatorioId) {
    try {
      const response = await fetch(`${this.baseURL}/recordatorio/${recordatorioId}/mostrar/`);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al mostrar recordatorio:', error);
      throw error;
    }
  }

  // Desactivar un recordatorio
  async desactivarRecordatorio(recordatorioId) {
    try {
      const response = await fetch(`${this.baseURL}/recordatorio/${recordatorioId}/desactivar/`, {
        method: 'PUT'
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error al desactivar recordatorio:', error);
      throw error;
    }
  }

  // Obtener todas las notificaciones pendientes
  async obtenerNotificacionesPendientes(tratamientoId) {
    try {
      const response = await fetch(`${this.baseURL}/${tratamientoId}/notificaciones-pendientes/`);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al obtener notificaciones pendientes:', error);
      throw error;
    }
  }
}

export default NotificationService;
