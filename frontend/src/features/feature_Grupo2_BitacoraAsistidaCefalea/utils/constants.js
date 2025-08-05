export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const EPISODIOS_ENDPOINT = '/evaluaciones/episodios/';
export const USUARIOS_ENDPOINT = '/usuarios/';
export const MI_PERFIL_ENDPOINT = '/usuarios/mi_perfil/';

// Tokens temporales - TODO: Implementar sistema de autenticación apropiado
export const TEMP_TOKEN_PACIENTE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjU1MjAzLCJpYXQiOjE3NTQyNTE2MDMsImp0aSI6ImQ3NmI3Nzc0NmMzYzQ0YzNiNWRiMTQzZDM3NzQwNmY3IiwidXNlcl9pZCI6IjU4In0.FolkG7Bocyx_5t8tWXfdZ16RioaguiEJoKL3oDWEuDQ";

export const TEMP_TOKEN_MEDICO = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjUwOTcwLCJpYXQiOjE3NTQyNDczNzAsImp0aSI6ImRkNGM2MzkzZDY1ZjQwMTFhZDhjM2EyODAzOTE2NTYyIiwidXNlcl9pZCI6IjEifQ.uy39PM_JfpB0WAuPAc_pvTbjvKCzORkHSV6uD3nafqk";

// Token por defecto (mantiene compatibilidad)
export const TEMP_TOKEN = TEMP_TOKEN_PACIENTE;

// Constantes del formulario de registro de cefalea
export const INITIAL_FORM_DATA = {
    duracion_cefalea_horas: '',
    severidad: '',
    localizacion: '',
    caracter_dolor: '',
    empeora_actividad: '',
    nauseas_vomitos: '',
    fotofobia: '',
    fonofobia: '',
    presencia_aura: '',
    sintomas_aura: '',
    duracion_aura_minutos: '',
    en_menstruacion: '',
    anticonceptivos: ''
};

export const BOOLEAN_FIELDS = [
    'empeora_actividad',
    'nauseas_vomitos',
    'fotofobia',
    'fonofobia',
    'presencia_aura',
    'en_menstruacion',
    'anticonceptivos'
];

export const REQUIRED_FIELDS = [
    'duracion_cefalea_horas',
    'severidad',
    'localizacion',
    'caracter_dolor'
];
