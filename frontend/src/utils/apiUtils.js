
// Importaciones de constantes y funciones auxiliares
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const EPISODIOS_ENDPOINT = '/evaluaciones/episodios/';
const TEMP_TOKEN_PACIENTE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwODg2LCJpYXQiOjE3NTQyNDcyODYsImp0aSI6IjIzOGE2OTc5Y2EzZTRiMzE5MzI4ZTEyMDQ4ZWRmMTRkIiwidXNlcl9pZCI6IjU4In0.EQafLInInPtkzjXy9Tw0tKSVoZkJ2WcqzWnzQZvC1EA";
const TEMP_TOKEN_MEDICO = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwOTcwLCJpYXQiOjE3NTQyNDczNzAsImp0aSI6ImRkNGM2MzkzZDY1ZjQwMTFhZDhjM2EyODAzOTE2NTYyIiwidXNlcl9pZCI6IjEifQ.uy39PM_JfpB0WAuPAc_pvTbjvKCzORkHSV6uD3nafqk";

// Funciones auxiliares
export const getApiUrl = (endpoint) => {
    return `${BASE_URL}${endpoint}`;
};

export const isTokenExpired = (token) => {
    if (!token) return true;

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    } catch (error) {
        console.error('Error al verificar token:', error);
        return true;
    }
};

export const getAuthHeaders = (token = null, userType = 'paciente') => {
    const defaultToken = token || (userType === 'medico' ? TEMP_TOKEN_MEDICO : TEMP_TOKEN_PACIENTE);

    if (isTokenExpired(defaultToken)) {
        console.warn(`Token ${userType} ha expirado`);
    }

    return {
        'Content-Type': 'application/json',
        'Authorization': defaultToken ? `Bearer ${defaultToken}` : '',
    };
};

export const parseApiResponse = (data) => {
    console.log('Parseando respuesta API:', data);

    if (Array.isArray(data)) {
        console.log('Data es array directo, devolviendo:', data);
        return data;
    }

    const possibleArrayPaths = ['results', 'episodios', 'data'];
    for (const path of possibleArrayPaths) {
        if (data && Array.isArray(data[path])) {
            console.log(`Encontrado array en ${path}:`, data[path]);
            return data[path];
        }
    }

    console.error('Estructura de datos inesperada:', data);
    console.error('Tipo de data:', typeof data);
    console.error('Keys disponibles:', Object.keys(data || {}));

    // Si no encontramos un array, pero data existe, intentar devolverlo tal como está
    if (data) {
        console.warn('Devolviendo data sin parsear:', data);
        return data;
    }

    throw new Error('La respuesta del servidor no tiene el formato esperado');
};

export const fetchEpisodiosPaciente = async (token = null) => {
    return fetchEpisodios(token, 'paciente');
};

export const fetchEpisodios = async (token = null, userType = 'paciente') => {
    try {
        const url = getApiUrl(EPISODIOS_ENDPOINT);
        const headers = getAuthHeaders(token, userType);
        const defaultToken = token || (userType === 'medico' ? TEMP_TOKEN_MEDICO : TEMP_TOKEN_PACIENTE);

        // Verificar si el token ha expirado antes de hacer la petición
        if (isTokenExpired(defaultToken)) {
            console.warn('Token expirado detectado, retornando datos de prueba');
            return getMockEpisodios();
        }

        console.log('Haciendo request a:', url);
        console.log('Con headers:', headers);

        const response = await fetch(url, {
            method: 'GET',
            headers: headers
        });

        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response body:', errorText);

            if (response.status === 401) {
                console.warn('Error 401: Token expirado o inválido, retornando datos de prueba');
                return getMockEpisodios();
            }

            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Raw data from API:', data);

        const parsedData = parseApiResponse(data);
        console.log('Parsed data:', parsedData);

        return parsedData;
    } catch (error) {
        console.error('Error al obtener episodios:', error);

        // Si hay error de red o token, retornar datos de prueba
        if (error.message.includes('401') || error.message.includes('fetch')) {
            console.warn('Retornando datos de prueba debido a error de autenticación');
            return getMockEpisodios();
        }

        throw error;
    }
};
export const fetchEpisodiosMedico = async (token = null) => {
    return fetchEpisodios(token, 'medico');
};

// Datos de prueba para cuando no hay tokens válidos
export const getMockEpisodios = () => {
    console.log('Retornando datos de prueba de episodios');
    return [
        {
            id: 1,
            fecha: "2025-08-03",
            severidad: "leve",
            duracion: "6h",
            localizacion: "unilateral",
            desencadenante: "pulsátil",
            sintomas_acompanantes: ["náuseas"],
            tratamiento_usado: "paracetamol",
            efectividad_tratamiento: 7
        },
        {
            id: 2,
            fecha: "2025-08-03",
            severidad: "leve",
            duracion: "69h",
            localizacion: "unilateral",
            desencadenante: "pulsátil",
            sintomas_acompanantes: [],
            tratamiento_usado: null,
            efectividad_tratamiento: null
        },
        {
            id: 3,
            fecha: "2025-08-03",
            severidad: "leve",
            duracion: "1h",
            localizacion: "bilateral",
            desencadenante: "opresivo",
            sintomas_acompanantes: [],
            tratamiento_usado: null,
            efectividad_tratamiento: null
        },
        {
            id: 4,
            fecha: "2025-08-02",
            severidad: "leve",
            duracion: "72h",
            localizacion: "unilateral",
            desencadenante: "pulsátil",
            sintomas_acompanantes: [],
            tratamiento_usado: null,
            efectividad_tratamiento: null
        }
    ];
};
