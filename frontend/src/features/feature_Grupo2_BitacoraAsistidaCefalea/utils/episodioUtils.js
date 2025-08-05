import { BOOLEAN_FIELDS, REQUIRED_FIELDS } from './constants.js';

export const transformEpisodio = (episodio) => ({
    ...episodio,
    creado_en: episodio.creado_en ? new Date(episodio.creado_en).toLocaleString() : '-',
    empeora_actividad: episodio.empeora_actividad ? 'Sí' : 'No',
    nauseas_vomitos: episodio.nauseas_vomitos ? 'Sí' : 'No',
    fotofobia: episodio.fotofobia ? 'Sí' : 'No',
    fonofobia: episodio.fonofobia ? 'Sí' : 'No',
    presencia_aura: episodio.presencia_aura ? 'Sí' : 'No',
    en_menstruacion: episodio.en_menstruacion ? 'Sí' : 'No',
    anticonceptivos: episodio.anticonceptivos ? 'Sí' : 'No',
    sintomas_aura: episodio.sintomas_aura || '-'
});

/**
 * Convierte string "Sí"/"No" a booleano
 * @param {string} value - Valor a convertir
 * @returns {boolean} Valor booleano
 */
export const convertStringToBoolean = (value) => {
    return value === 'Sí' || value === 'Si';
};

/**
 * Transforma los datos del formulario para enviar a la API
 * @param {Object} formData - Datos del formulario
 * @param {Object} userInfo - Información del usuario
 * @returns {Object} Datos transformados para la API
 */
export const transformFormDataForAPI = (formData, userInfo) => {
    const transformedData = { ...formData };

    // Transformar campos booleanos
    BOOLEAN_FIELDS.forEach(field => {
        transformedData[field] = convertStringToBoolean(transformedData[field]);
    });

    // Campos específicos para hombres
    if (userInfo?.genero === 'M') {
        transformedData.en_menstruacion = false;
        transformedData.anticonceptivos = false;
    }

    // Convertir campos numéricos
    if (transformedData.duracion_cefalea_horas) {
        transformedData.duracion_cefalea_horas = parseInt(transformedData.duracion_cefalea_horas);
    }

    transformedData.duracion_aura_minutos = transformedData.duracion_aura_minutos
        ? parseInt(transformedData.duracion_aura_minutos)
        : 0;

    // Manejar síntomas del aura
    if (!transformedData.presencia_aura) {
        transformedData.sintomas_aura = "";
        transformedData.duracion_aura_minutos = 0;
    } else if (!transformedData.sintomas_aura) {
        transformedData.sintomas_aura = "";
    }

    return transformedData;
};

/**
 * Valida los datos del formulario
 * @param {Object} formData - Datos del formulario a validar
 * @throws {Error} Si la validación falla
 */
export const validateEpisodioForm = (formData) => {
    const missingFields = REQUIRED_FIELDS.filter(field => !formData[field]);

    if (missingFields.length > 0) {
        throw new Error(`Campos requeridos faltantes: ${missingFields.join(', ')}`);
    }

    const duracion = parseInt(formData.duracion_cefalea_horas);
    if (isNaN(duracion) || duracion < 1 || duracion > 72) {
        throw new Error('La duración de la cefalea debe estar entre 1 y 72 horas.');
    }

    if (formData.presencia_aura === 'Sí' && formData.duracion_aura_minutos && parseInt(formData.duracion_aura_minutos) === 0) {
        throw new Error('Si hay presencia de aura, debe especificar una duración mayor a 0 minutos.');
    }
};

export const COLUMNAS_EPISODIOS = [
    { key: 'creado_en', header: 'Fecha de Registro' },
    { key: 'categoria_diagnostica', header: 'Categoría Diagnóstica' },
    { key: 'duracion_cefalea_horas', header: 'Duración Cefalea (horas)' },
    { key: 'severidad', header: 'Severidad del Dolor' },
    { key: 'localizacion', header: 'Localización del Dolor' },
    { key: 'caracter_dolor', header: 'Carácter del Dolor' },
    { key: 'empeora_actividad', header: 'Empeora con Actividad' },
    { key: 'nauseas_vomitos', header: 'Náuseas o Vómitos' },
    { key: 'fotofobia', header: 'Sensibilidad a la Luz' },
    { key: 'fonofobia', header: 'Sensibilidad al Sonido' },
    { key: 'presencia_aura', header: 'Presencia de Aura' },
    { key: 'sintomas_aura', header: 'Síntomas del Aura' },
    { key: 'duracion_aura_minutos', header: 'Duración del Aura (min)' },
    { key: 'en_menstruacion', header: 'En menstruación' },
    { key: 'anticonceptivos', header: 'Anticonceptivos' }
];

// Columnas específicas para la vista del médico (mismas columnas por ahora)
export const COLUMNAS_EPISODIOS_MEDICO = COLUMNAS_EPISODIOS;

// Función específica para transformar episodios en la vista del médico
export const transformEpisodioMedico = transformEpisodio;
