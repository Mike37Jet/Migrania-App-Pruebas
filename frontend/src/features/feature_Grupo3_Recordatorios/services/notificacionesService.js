
// Servicio para consumir las APIs de notificaciones
const API_BASE_URL = 'http://localhost:8000/api';

export class NotificacionesService {
  // Avisar al backend que una alerta no fue confirmada (para generar segunda/tercera alerta)
  static async marcarAlertaNoConfirmada(alertaId) {
    try {
      let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
      if (!token) throw new Error('No se encontró token de sesión');
      const response = await fetch(`${API_BASE_URL}/tratamientos/alerta/${alertaId}/no-confirmada/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('❌ Error al marcar alerta como no confirmada:', error);
      throw error;
    }
  }
  // Obtener el pacienteId usando el endpoint protegido y el token de sesión
  static async obtenerPacienteId() {
    try {
      let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No se encontró token de sesión');
      }
      const response = await fetch(`${API_BASE_URL}/tratamientos/mi-paciente-id/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      // Se espera que el backend retorne { paciente_id: ... }
      return data.paciente_id;
    } catch (error) {
      console.error('Error obteniendo pacienteId:', error);
      return null;
    }
  }
  // Obtener alertas por paciente
  static async obtenerAlertasPorPaciente(pacienteId) {
    const response = await fetch(`${API_BASE_URL}/tratamientos/alertas-por-paciente/${pacienteId}/`);
    if (!response.ok) throw new Error('Error al obtener alertas por paciente');
    return await response.json();
  }

  // Obtener recordatorios por paciente
  static async obtenerRecordatoriosPorPaciente(pacienteId) {
    const response = await fetch(`${API_BASE_URL}/tratamientos/recordatorios-por-paciente/${pacienteId}/`);
    if (!response.ok) throw new Error('Error al obtener recordatorios por paciente');
    return await response.json();
  }
  
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
      console.error('❌ Error obteniendo notificaciones pendientes:', error);
      // Devolver estructura vacía para evitar crashes del frontend
      return {
        alertas: [],
        recordatorios: [],
        total: 0
      };
    }
  }

  // Obtener alertas por tratamiento - usando endpoint real de notificaciones pendientes
  static async obtenerAlertas(tratamientoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/notificaciones-pendientes/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data.alertas || []; // Devolver solo las alertas
    } catch (error) {
      console.error('Error obteniendo alertas:', error);
      // En lugar de lanzar error, devolver array vacío para fallback
      return [];
    }
  }

  // Obtener recordatorios por tratamiento - usando endpoint real de notificaciones pendientes
  static async obtenerRecordatorios(tratamientoId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/notificaciones-pendientes/`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      return data.recordatorios || []; // Devolver solo los recordatorios
    } catch (error) {
      console.error('Error obteniendo recordatorios:', error);
      // En lugar de lanzar error, devolver array vacío para fallback
      return [];
    }
  }

  // Marcar alerta como confirmada usando el endpoint correcto
  static async confirmarAlerta(alertaId) {
    try {
      // Validar que el ID no sea de prueba
      if (typeof alertaId === 'string' && alertaId.startsWith('test-')) {
        console.warn('🧪 Intentando confirmar alerta de prueba, simulando éxito:', alertaId);
        return { success: true, message: 'Alerta de prueba confirmada (simulado)' };
      }

      // Usar el token real del usuario autenticado
      let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No se encontró token de sesión');
      }

      const response = await fetch(`${API_BASE_URL}/tratamientos/alerta/${alertaId}/estado/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nuevo_estado: 'tomado',
          hora_confirmacion: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error confirmando alerta:', error);
      // Para desarrollo, simular confirmación exitosa en lugar de fallar
      console.log('🧪 Simulando confirmación de alerta exitosa para desarrollo');
      return { success: true, message: 'Alerta confirmada (simulado)', alertaId };
    }
  }

  // Marcar alerta como NO tomada
  static async confirmarAlertaNoTomada(alertaId) {
    try {
      // Validar que el ID no sea de prueba
      if (typeof alertaId === 'string' && alertaId.startsWith('test-')) {
        console.warn('🧪 Intentando confirmar alerta NO tomada de prueba, simulando éxito:', alertaId);
        return { success: true, message: 'Alerta de prueba marcada como NO tomada (simulado)' };
      }

      const TEMP_TOKEN_PACIENTE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwODg2LCJpYXQiOjE3NTQyNDcyODYsImp0aSI6IjIzOGE2OTc5Y2EzZTRiMzE5MzI4ZTEyMDQ4ZWRmMTRkIiwidXNlcl9pZCI6IjU4In0.EQafLInInPtkzjXy9Tw0tKSVoZkJ2WcqzWnzQZvC1EA";

      const response = await fetch(`${API_BASE_URL}/tratamientos/alerta/${alertaId}/estado/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${TEMP_TOKEN_PACIENTE}`
        },
        body: JSON.stringify({
          nuevo_estado: 'no_tomado',
          hora_confirmacion: new Date().toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error confirmando alerta como NO tomada:', error);
      // Para desarrollo, simular confirmación exitosa en lugar de fallar
      console.log('🧪 Simulando confirmación de alerta NO tomada exitosa para desarrollo');
      return { success: true, message: 'Alerta marcada como NO tomada (simulado)', alertaId };
    }
  }

  // Procesar notificaciones para reenvío automático
  static async procesarNotificaciones(tratamientoId) {
    console.log(`🔧 Procesando notificaciones para tratamiento ID: ${tratamientoId}`);
    
    try {
      // Intentar obtener token del localStorage primero (del login real)
      let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
      
      // Si no hay token del login, usar el temporal para desarrollo
      const TEMP_TOKEN_PACIENTE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwODg2LCJpYXQiOjE3NTQyNDcyODYsImp0aSI6IjIzOGE2OTc5Y2EzZTRiMzE5MzI4ZTEyMDQ4ZWRmMTRkIiwidXNlcl9pZCI6IjU4In0.EQafLInInPtkzjXy9Tw0tKSVoZkJ2WcqzWnzQZvC1EA";
      
      if (!token) {
        console.log('🔑 No hay token en localStorage, usando token temporal');
        token = TEMP_TOKEN_PACIENTE;
      } else {
        console.log('🔑 Usando token del localStorage');
      }
      
      // Función para verificar si el token ha expirado
      const isTokenExpired = (token) => {
        if (!token) return true;
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const currentTime = Math.floor(Date.now() / 1000);
          return payload.exp < currentTime;
        } catch (error) {
          return true;
        }
      };

      // Si el token está expirado, simular procesamiento exitoso
      if (isTokenExpired(token)) {
        console.warn('⚠️ Token expirado, simulando procesamiento de notificaciones');
        return { procesadas: 0, mensaje: 'Procesamiento simulado (token expirado)' };
      }
      
      console.log(`📡 Llamando a API: POST /tratamientos/${tratamientoId}/procesar-notificaciones/`);
      
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/procesar-notificaciones/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(`📊 Respuesta del servidor: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Error HTTP ${response.status}:`, errorText);
        throw new Error(`Error ${response.status}: ${response.statusText} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`✅ Procesamiento exitoso para tratamiento ${tratamientoId}:`, data);
      return data;
    } catch (error) {
      console.error(`❌ Error procesando notificaciones para tratamiento ${tratamientoId}:`, error);
      
      // Verificar si es un error de red, servidor, etc.
      if (error.message.includes('500')) {
        console.error('🚨 Error 500 del servidor - posible problema en el backend');
      } else if (error.message.includes('401')) {
        console.error('🔐 Error 401 - problema de autenticación');
      } else if (error.message.includes('404')) {
        console.error('🔍 Error 404 - endpoint no encontrado');
      }
      
      // Para desarrollo, no simular éxito si hay errores reales
      throw error;
    }
  }

  // Generar notificaciones automáticamente si no existen
  static async generarNotificacionesAutomaticas(tratamientoId) {
    console.log(`🏭 Generando notificaciones automáticas para tratamiento ID: ${tratamientoId}`);
    
    try {
      let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
      const TEMP_TOKEN_PACIENTE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwODg2LCJpYXQiOjE3NTQyNDcyODYsImp0aSI6IjIzOGE2OTc5Y2EzZTRiMzE5MzI4ZTEyMDQ4ZWRmMTRkIiwidXNlcl9pZCI6IjU4In0.EQafLInInPtkzjXy9Tw0tKSVoZkJ2WcqzWnzQZvC1EA";
      
      if (!token) {
        token = TEMP_TOKEN_PACIENTE;
      }
      
      const response = await fetch(`${API_BASE_URL}/tratamientos/${tratamientoId}/generar-notificaciones/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`✅ Notificaciones generadas para tratamiento ${tratamientoId}:`, data);
      return data;
    } catch (error) {
      console.error(`❌ Error generando notificaciones para tratamiento ${tratamientoId}:`, error);
      throw error;
    }
  }

  // Desactivar recordatorio usando el endpoint correcto
  static async desactivarRecordatorio(recordatorioId) {
    try {
      // Validar que el ID no sea de prueba
      if (typeof recordatorioId === 'string' && recordatorioId.startsWith('test-')) {
        console.warn('🧪 Intentando desactivar recordatorio de prueba, simulando éxito:', recordatorioId);
        return { success: true, message: 'Recordatorio de prueba desactivado (simulado)' };
      }

      // Usar el token real del usuario autenticado
      let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No se encontró token de sesión');
      }

      const response = await fetch(`${API_BASE_URL}/tratamientos/recordatorio/${recordatorioId}/desactivar/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error desactivando recordatorio:', error);
      // Para desarrollo, simular desactivación exitosa en lugar de fallar
      console.log('🧪 Simulando desactivación de recordatorio exitosa para desarrollo');
      return { success: true, message: 'Recordatorio desactivado (simulado)', recordatorioId };
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
    // Solo mostrar notificaciones si los datos reales existen
    if (!item || !item.id) return null;
    const tiempoRelativo = this.calcularTiempoRelativo(item.fecha_hora || item.fecha_creacion || item.fecha_inicio);

    if (tipo === 'alerta') {
      if (!item.mensaje && !item.descripcion && !item.medicamento_nombre) return null;
      return {
        id: item.id,
        tipo: 'alerta',
        titulo: item.titulo || '',
        mensaje: item.mensaje || item.descripcion || '',
        tiempo: tiempoRelativo,
        activa: item.activa,
        confirmada: item.confirmada
      };
    }
    if (tipo === 'recordatorio') {
      if (!item.mensaje && !item.descripcion) return null;
      return {
        id: item.id,
        tipo: 'recordatorio',
        titulo: item.titulo || '',
        mensaje: item.mensaje || item.descripcion || '',
        tiempo: tiempoRelativo,
        activo: item.activo
      };
    }
    // Si no es alerta ni recordatorio, ignorar
    return null;
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

    // Función de testing para simular notificaciones pendientes
    static simularNotificacionesPendientes(tratamientoId, incluirAlerta = false, incluirRecordatorio = false) {
        const notificacionesSimuladas = {
            alertas: [],
            recordatorios: [],
            total: 0
        };

        if (incluirAlerta) {
            notificacionesSimuladas.alertas.push({
                id: `test-alerta-${Date.now()}`,
                mensaje: 'Es hora de tomar tu medicamento Ibuprofeno 400mg',
                estado: 'sin_confirmar',
                fecha_hora: new Date().toISOString(),
                duracion: 15,
                numero_alerta: 1
            });
            notificacionesSimuladas.total++;
        }

        if (incluirRecordatorio) {
            notificacionesSimuladas.recordatorios.push({
                id: `test-recordatorio-${Date.now()}`,
                mensaje: 'Recordatorio: Mantén una rutina regular de sueño',
                estado: 'activo',
                fecha_hora: new Date().toISOString()
            });
            notificacionesSimuladas.total++;
        }

        console.log('📦 Notificaciones simuladas:', notificacionesSimuladas);
        return Promise.resolve(notificacionesSimuladas);
    }

    // Obtener tratamientos activos del paciente
    static async obtenerTratamientosActivos() {
        try {
            // Intentar obtener token del localStorage primero (del login real)
            let token = localStorage.getItem('access_token') || localStorage.getItem('access') || localStorage.getItem('authToken');
            
            // Si no hay token del login, usar el temporal para desarrollo
            const TEMP_TOKEN_PACIENTE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwODg2LCJpYXQiOjE3NTQyNDcyODYsImp0aSI6IjIzOGE2OTc5Y2EzZTRiMzE5MzI4ZTEyMDQ4ZWRmMTRkIiwidXNlcl9pZCI6IjU4In0.EQafLInInPtkzjXy9Tw0tKSVoZkJ2WcqzWnzQZvC1EA";
            
            if (!token) {
                token = TEMP_TOKEN_PACIENTE;
                console.log('🔑 Usando token temporal para desarrollo');
            } else {
                console.log('🔑 Usando token del login actual');
            }
            
            // Función para verificar si el token ha expirado
            const isTokenExpired = (token) => {
                if (!token) return true;
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    const currentTime = Math.floor(Date.now() / 1000);
                    return payload.exp < currentTime;
                } catch (error) {
                    return true;
                }
            };

            // Si el token está expirado, ir directamente al fallback
            if (isTokenExpired(token)) {
                console.warn('Token ha expirado, usando datos de desarrollo');
                return [{
                    id: 1,  // ID de prueba que coincide con generar_notificaciones
                    activo: true,
                    tipo_migraña: 'Episódica',
                    fecha_inicio: new Date().toISOString()
                }];
            }

            const response = await fetch(`${API_BASE_URL}/tratamientos/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('📋 Respuesta de tratamientos:', data);
            
            // Manejar diferentes formatos de respuesta de la API
            let tratamientos = [];
            if (Array.isArray(data)) {
                tratamientos = data;
            } else if (data && Array.isArray(data.results)) {
                tratamientos = data.results;
            } else if (data && Array.isArray(data.tratamientos)) {
                tratamientos = data.tratamientos;
            } else if (data && typeof data === 'object') {
                // Si es un objeto único, convertirlo en array
                tratamientos = [data];
            } else {
                console.warn('Formato de respuesta inesperado:', data);
                tratamientos = [];
            }
            
            // Filtrar solo tratamientos activos
            const tratamientosActivos = tratamientos.filter(t => t && t.activo === true);
            
            return tratamientosActivos.length > 0 ? tratamientosActivos : [{
                id: 1,  // Fallback al tratamiento de prueba
                activo: true,
                tipo_migraña: 'Episódica',
                fecha_inicio: new Date().toISOString()
            }];

        } catch (error) {
            console.error('Error obteniendo tratamientos activos:', error);
            
            // Fallback para desarrollo - usar el tratamiento de prueba que coincide con generar_notificaciones
            return [{
                id: 1,  // ID de prueba
                activo: true,
                tipo_migraña: 'Episódica',
                fecha_inicio: new Date().toISOString()
            }];
        }
    }
}

export default NotificacionesService;
