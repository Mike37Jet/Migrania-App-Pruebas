import { BASE_URL, TEMP_TOKEN, TEMP_TOKEN_PACIENTE, TEMP_TOKEN_MEDICO, MI_PERFIL_ENDPOINT, EPISODIOS_ENDPOINT } from './constants.js';

export const parseApiResponse = (data) => {
    if (Array.isArray(data)) {
        return data;
    }

    const possibleArrayPaths = ['results', 'episodios', 'data'];
    for (const path of possibleArrayPaths) {
        if (data && Array.isArray(data[path])) {
            return data[path];
        }
    }

    console.error('Estructura de datos inesperada:', data);
    throw new Error('La respuesta del servidor no tiene el formato esperado');
};

export const getErrorMessage = (error, response, context = 'paciente') => {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return 'No se puede conectar al servidor. Verifica que el backend esté ejecutándose.';
    }

    if (response) {
        switch (response.status) {
            case 401:
                return context === 'medico'
                    ? 'No autorizado. Por favor, inicia sesión nuevamente.'
                    : 'Sesión expirada. Por favor, inicia sesión nuevamente.';
            case 403:
                return context === 'medico'
                    ? 'No tienes permisos para ver los episodios de este paciente.'
                    : 'No tienes permisos para ver los episodios.';
            case 404:
                return context === 'medico'
                    ? 'Paciente no encontrado.'
                    : 'Episodios no encontrados.';
            default:
                return `Error ${response.status}: ${response.statusText}`;
        }
    }

    return `Error al cargar los episodios: ${error.message}`;
};

// Función específica para médicos (mantiene compatibilidad)
export const getErrorMessageMedico = (error, response) => {
    return getErrorMessage(error, response, 'medico');
};

/**
 * Construye la URL completa de la API
 * @param {string} endpoint - Endpoint de la API
 * @returns {string} URL completa
 */
export const getApiUrl = (endpoint) => {
    return `${BASE_URL}${endpoint}`;
};

/**
 * Obtiene los headers de autenticación
 * @param {string} token - Token de autenticación (opcional, usa TEMP_TOKEN_PACIENTE por defecto)
 * @param {string} userType - Tipo de usuario ('paciente' o 'medico')
 * @returns {Object} Headers con autenticación
 */
export const getAuthHeaders = (token = null, userType = 'paciente') => {
    const defaultToken = token || (userType === 'medico' ? TEMP_TOKEN_MEDICO : TEMP_TOKEN_PACIENTE);
    return {
        'Content-Type': 'application/json',
        'Authorization': defaultToken ? `Bearer ${defaultToken}` : '',
    };
};

/**
 * Obtiene información del usuario actual
 * @param {string} token - Token de autenticación (opcional)
 * @param {string} userType - Tipo de usuario ('paciente' o 'medico')
 * @returns {Promise<Object>} Información del usuario
 */
export const fetchUserInfo = async (token = null, userType = 'paciente') => {
    const response = await fetch(getApiUrl(MI_PERFIL_ENDPOINT), {
        method: 'GET',
        headers: getAuthHeaders(token, userType)
    });

    if (!response.ok) {
        console.error(`Error al obtener información del usuario:`, response.status);
        // Fallback para mostrar todos los campos
        return { genero: 'F', nombre_completo: 'Usuario' };
    }

    const userData = await response.json();
    console.log('Información del usuario:', userData);
    return userData;
};

/**
 * Maneja errores de API y lanza errores apropiados
 * @param {Response} response - Respuesta de la API
 * @param {Object} errorData - Datos de error de la respuesta
 * @throws {Error} Error con mensaje apropiado
 */
export const handleApiError = (response, errorData) => {
    if (response.status === 401) {
        throw new Error('No autorizado. Por favor, inicia sesión nuevamente.');
    } else if (response.status === 403) {
        throw new Error('No tienes permisos para crear episodios.');
    } else if (response.status === 400) {
        const errorMessages = Object.entries(errorData).map(([field, messages]) =>
            `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
        ).join('; ');
        throw new Error(`Error de validación: ${errorMessages}`);
    } else {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
};

/**
 * Crea un nuevo episodio de cefalea
 * @param {Object} episodioData - Datos del episodio
 * @param {string} token - Token de autenticación (opcional)
 * @param {string} userType - Tipo de usuario ('paciente' o 'medico')
 * @returns {Promise<Object>} Respuesta de la API
 */
export const createEpisodio = async (episodioData, token = null, userType = 'paciente') => {
    const response = await fetch(getApiUrl(EPISODIOS_ENDPOINT), {
        method: 'POST',
        headers: getAuthHeaders(token, userType),
        body: JSON.stringify(episodioData)
    });

    if (!response.ok) {
        const errorData = await response.json();
        handleApiError(response, errorData);
    }

    return await response.json();
};


// Funciones específicas para pacientes
export const fetchUserInfoPaciente = async (token = null) => {
    return fetchUserInfo(token, 'paciente');
};

export const createEpisodioPaciente = async (episodioData, token = null) => {
    return createEpisodio(episodioData, token, 'paciente');
};


// Funciones específicas para médicos
export const fetchUserInfoMedico = async (token = null) => {
    return fetchUserInfo(token, 'medico');
};

export const createEpisodioMedico = async (episodioData, token = null) => {
    return createEpisodio(episodioData, token, 'medico');
};


export const fetchPacienteInfo = async (pacienteId, baseUrl, token) => {
    try {
        const pacienteUrl = `${baseUrl}/usuarios/${pacienteId}/`;
        console.log('Intentando obtener información del paciente desde:', pacienteUrl);

        const response = await fetch(pacienteUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : '',
            }
        });

        console.log('Respuesta del API para paciente:', response.status, response.statusText);

        if (response.ok) {
            const pacienteData = await response.json();
            console.log('Datos completos del paciente:', pacienteData);

            // Intentar diferentes campos para obtener el nombre
            const nombre = pacienteData.first_name ||
                pacienteData.nombre ||
                pacienteData.username ||
                'Paciente';

            console.log('Nombre del paciente obtenido:', nombre);
            return nombre;
        } else {
            console.error('Error en la respuesta del API:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Detalles del error:', errorText);
            return 'Paciente';
        }
    } catch (error) {
        console.error('Error al obtener información del paciente:', error);
        return 'Paciente';
    }
};
