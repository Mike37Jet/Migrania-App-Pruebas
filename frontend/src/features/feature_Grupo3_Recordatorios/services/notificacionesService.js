// Servicio para consumir las APIs de notificaciones
const API_BASE_URL = 'http://localhost:8000/api';

export class NotificacionesService {
  
  // Obtener todas las notificaciones pendientes para un tratamiento
  static async obtenerNotificacionesPendientes(tratamientoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/notificaciones-pendientes/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error obteniendo notificaciones pendientes:', error);
      throw error;
    }
  }

  // Obtener alertas por tratamiento (versión de testing)
  static async obtenerAlertas(tratamientoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/alertas-test/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data.data || data; // Devolver solo los datos
    } catch (error) {
      console.error('Error obteniendo alertas:', error);
      throw error;
    }
  }

  // Obtener recordatorios por tratamiento (versión de testing)
  static async obtenerRecordatorios(tratamientoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/recordatorios-test/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data.data || data; // Devolver solo los datos
    } catch (error) {
      console.error('Error obteniendo recordatorios:', error);
      throw error;
    }
  }

  // Marcar alerta como confirmada
  static async confirmarAlerta(alertaId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/alertas/${alertaId}/confirmar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error confirmando alerta:', error);
      throw error;
    }
  }

  // Desactivar recordatorio
  static async desactivarRecordatorio(recordatorioId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/recordatorios/${recordatorioId}/desactivar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error desactivando recordatorio:', error);
      throw error;
    }
  }

  // Obtener estado de alerta (activa/inactiva)
  static async obtenerEstadoAlerta(alertaId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/alertas/${alertaId}/estado/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error obteniendo estado de alerta:', error);
      throw error;
    }
  }

  // Obtener próxima alerta para un tratamiento
  static async obtenerProximaAlerta(tratamientoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/siguiente-alerta/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error obteniendo próxima alerta:', error);
      throw error;
    }
  }

  // Formatear datos de API para el frontend
  static formatearNotificacion(item, tipo) {
    const tiempoRelativo = this.calcularTiempoRelativo(item.fecha_creacion || item.fecha_inicio);
    
    switch (tipo) {
      case 'alerta':
        return {
          id: item.id,
          tipo: 'medicacion',
          titulo: 'Es hora de prepararte para tu medicación',
          mensaje: `${item.medicamento_nombre} - ${item.descripcion}`,
          tiempo: tiempoRelativo,
          activa: item.activa,
          confirmada: item.confirmada
        };
      
      case 'recordatorio':
        return {
          id: item.id,
          tipo: 'recordatorio',
          titulo: 'Recuerda:',
          mensaje: item.descripcion,
          tiempo: tiempoRelativo,
          activo: item.activo
        };
      
      default:
        return {
          id: item.id,
          tipo: 'alerta',
          titulo: 'Notificación',
          mensaje: item.descripcion || 'Sin descripción',
          tiempo: tiempoRelativo
        };
    }
  }

  // Calcular tiempo relativo (ej: "2m", "1h", "3d")
  static calcularTiempoRelativo(fechaString) {
    if (!fechaString) return 'Ahora';
    
    const fecha = new Date(fechaString);
    const ahora = new Date();
    const diferencia = Math.abs(ahora - fecha);
    
    const minutos = Math.floor(diferencia / (1000 * 60));
    const horas = Math.floor(diferencia / (1000 * 60 * 60));
    const dias = Math.floor(diferencia / (1000 * 60 * 60 * 24));
    
    if (minutos < 60) {
      return `${minutos}m`;
    } else if (horas < 24) {
      return `${horas}h`;
    } else {
      return `${dias}d`;
    }
  }
    // Activar alerta inmediata para testing
    static async activarAlertaInmediata(tratamientoId, mensaje = null) {
        const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/activar-alerta-inmediata/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },  
            body: JSON.stringify({ mensaje })
        });
        return response.json();
    }

    // Confirmar alerta específica (nueva implementación)
    static async confirmarAlertaEspecifica(alertaId) {
        const response = await fetch(`${API_BASE_URL}/tratamientos/alertas/${alertaId}/confirmar/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return response.json();
    }
}

export default NotificacionesService;
