// Utilidades para manejo de fechas de episodios

/**
 * Obtiene la fecha de un episodio usando múltiples campos de respaldo
 * @param {Object} episodio - El objeto episodio
 * @returns {string|null} La fecha del episodio
 */
export const obtenerFechaEpisodio = (episodio) => {
    return episodio.fecha_inicio || episodio.creado_en || episodio.fecha;
};

/**
 * Limpia una fecha string removiendo partes innecesarias como la hora
 * @param {string} fechaString - La fecha como string
 * @returns {string} La fecha limpia
 */
export const limpiarFecha = (fechaString) => {
    if (!fechaString || typeof fechaString !== 'string') return fechaString;
    return fechaString.includes(',') ? fechaString.split(',')[0].trim() : fechaString;
};

/**
 * Verifica si una fecha es válida
 * @param {string} fecha - La fecha a validar
 * @returns {boolean} True si la fecha es válida
 */
export const esFechaValida = (fecha) => {
    const dateObj = new Date(fecha);
    return !isNaN(dateObj.getTime());
};

/**
 * Compara dos episodios por fecha (más reciente primero)
 * @param {Object} episodioA - Primer episodio
 * @param {Object} episodioB - Segundo episodio
 * @returns {number} Resultado de la comparación
 */
export const compararFechas = (episodioA, episodioB) => {
    try {
        const fechaA = limpiarFecha(obtenerFechaEpisodio(episodioA));
        const fechaB = limpiarFecha(obtenerFechaEpisodio(episodioB));

        if (!esFechaValida(fechaA)) return 1;
        if (!esFechaValida(fechaB)) return -1;

        return new Date(fechaB).getTime() - new Date(fechaA).getTime();
    } catch (error) {
        console.error('Error al ordenar fechas:', error);
        return 0;
    }
};

/**
 * Formatea una fecha para mostrar en formato español (dd/mm/yyyy)
 * @param {string} fechaString - La fecha como string
 * @returns {string} La fecha formateada
 */
export const formatearFecha = (fechaString) => {
    if (!fechaString) return 'Fecha no disponible';

    try {
        const fechaLimpia = limpiarFecha(fechaString);
        const fecha = new Date(fechaLimpia);

        if (!esFechaValida(fechaLimpia)) {
            console.warn('Fecha inválida recibida:', fechaString);
            return 'Fecha inválida';
        }

        return fecha.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        console.error('Error al formatear fecha:', error, fechaString);
        return 'Error en fecha';
    }
};
