import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '@/common/components/Header.jsx';
import classes from '@/features/feature_Grupo2_BitacoraAsistidaCefalea/styles/bitacora.module.css';
import { INITIAL_FORM_DATA } from '../utils/constants.js';
import { fetchUserInfoPaciente, createEpisodioPaciente, getErrorMessage } from '../utils/apiUtils.js';
import { transformFormDataForAPI, validateEpisodioForm } from '../utils/episodioUtils.js';

export default function IngresarCefalea() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState(INITIAL_FORM_DATA);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [userInfo, setUserInfo] = useState(null);
    const [loadingUser, setLoadingUser] = useState(true);

    // Obtener información del usuario
    useEffect(() => {
        const loadUserInfo = async () => {
            try {
                setLoadingUser(true);
                const userData = await fetchUserInfoPaciente();
                setUserInfo(userData);
            } catch (err) {
                console.error('Error al obtener información del usuario:', err);
                // Fallback para mostrar todos los campos
                setUserInfo({ genero: 'F', nombre_completo: 'Usuario' });
            } finally {
                setLoadingUser(false);
            }
        };

        loadUserInfo();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const resetForm = () => {
        setFormData(INITIAL_FORM_DATA);
    };

    const showSuccessAndReset = () => {
        setSuccess(true);
        resetForm();
        setTimeout(() => {
            setSuccess(false);
        }, 3000);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);
            setError(null);
            setSuccess(false);

            validateEpisodioForm(formData);
            const apiData = transformFormDataForAPI(formData, userInfo);

            console.log('Datos del formulario original:', formData);
            console.log('Datos transformados para la API:', apiData);

            const responseData = await createEpisodioPaciente(apiData);
            console.log('Episodio creado exitosamente:', responseData);
            showSuccessAndReset();

        } catch (err) {
            console.error('Error al crear episodio:', err);
            setError(getErrorMessage(err));
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/bitacora-paciente');
    };

    const renderLoadingState = () => (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            Cargando información del usuario...
        </div>
    );

    const renderSubmissionState = () => (
        <>
            {loading && (
                <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                    Guardando episodio...
                </div>
            )}

            {error && (
                <div style={{
                    padding: '20px',
                    color: 'red',
                    textAlign: 'center',
                    background: '#ffebee',
                    border: '1px solid #ffcdd2',
                    borderRadius: '4px',
                    margin: '20px 0'
                }}>
                    {error}
                </div>
            )}

            {success && (
                <div style={{
                    padding: '20px',
                    color: 'green',
                    textAlign: 'center',
                    background: '#e8f5e8',
                    border: '1px solid #c8e6c9',
                    borderRadius: '4px',
                    margin: '20px 0'
                }}>
                    ¡Episodio registrado exitosamente!
                </div>
            )}
        </>
    );

    return (
        <div>
            <Header
                title="Bitácora"
                onBack={() => navigate('/bitacora-paciente')}
            />

            <div className="form-container">
                <h2 className="form-title">
                    Registrar nuevo episodio
                </h2>

                {loadingUser && renderLoadingState()}
                {renderSubmissionState()}

                {!loadingUser && userInfo && (
                    <form onSubmit={handleSubmit}>
                        <div className={classes.formGrid}>

                            <div className="form-field">
                                <label htmlFor="duracion_cefalea_horas" className={classes.labelStyled}>Duración (h) *</label>
                                <input
                                    type="number"
                                    id="duracion_cefalea_horas"
                                    name="duracion_cefalea_horas"
                                    placeholder="Ej: 5"
                                    min="1"
                                    max="72"
                                    value={formData.duracion_cefalea_horas}
                                    onChange={handleInputChange}
                                    className={classes.inputDefault}
                                    required
                                />
                            </div>

                            <div className="form-field">
                                <label htmlFor="severidad" className={classes.labelStyled}>Severidad *</label>
                                <select
                                    id="severidad"
                                    name="severidad"
                                    value={formData.severidad}
                                    onChange={handleInputChange}
                                    className={classes.selectDefault}
                                    required
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Leve">Leve</option>
                                    <option value="Moderada">Moderada</option>
                                    <option value="Severa">Severa</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="caracter_dolor" className={classes.labelStyled}>Carácter *</label>
                                <select
                                    id="caracter_dolor"
                                    name="caracter_dolor"
                                    value={formData.caracter_dolor}
                                    onChange={handleInputChange}
                                    className={classes.selectDefault}
                                    required
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Pulsátil">Pulsátil</option>
                                    <option value="Opresivo">Opresivo</option>
                                    <option value="Punzante">Punzante</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="localizacion" className={classes.labelStyled}>Localización *</label>
                                <select
                                    id="localizacion"
                                    name="localizacion"
                                    value={formData.localizacion}
                                    onChange={handleInputChange}
                                    className={classes.selectDefault}
                                    required
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Unilateral">Unilateral</option>
                                    <option value="Bilateral">Bilateral</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="empeora_actividad" className={classes.labelStyled}>Empeora con actividad</label>
                                <select
                                    id="empeora_actividad"
                                    name="empeora_actividad"
                                    value={formData.empeora_actividad}
                                    onChange={handleInputChange}
                                    className={`${classes.selectDefault} ${formData.empeora_actividad === '' ? classes.selectPlaceholder : ''}`}
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Sí">Sí</option>
                                    <option value="No">No</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="nauseas_vomitos" className={classes.labelStyled}>Náuseas o vómitos</label>
                                <select
                                    id="nauseas_vomitos"
                                    name="nauseas_vomitos"
                                    value={formData.nauseas_vomitos}
                                    onChange={handleInputChange}
                                    className={`${classes.selectDefault} ${formData.nauseas_vomitos === '' ? classes.selectPlaceholder : ''}`}
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Sí">Sí</option>
                                    <option value="No">No</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="fotofobia" className={classes.labelStyled}>Sensibilidad a la luz</label>
                                <select
                                    id="fotofobia"
                                    name="fotofobia"
                                    value={formData.fotofobia}
                                    onChange={handleInputChange}
                                    className={`${classes.selectDefault} ${formData.fotofobia === '' ? classes.selectPlaceholder : ''}`}
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Sí">Sí</option>
                                    <option value="No">No</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="fonofobia" className={classes.labelStyled}>Sensibilidad al sonido</label>
                                <select
                                    id="fonofobia"
                                    name="fonofobia"
                                    value={formData.fonofobia}
                                    onChange={handleInputChange}
                                    className={`${classes.selectDefault} ${formData.fonofobia === '' ? classes.selectPlaceholder : ''}`}
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Sí">Sí</option>
                                    <option value="No">No</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="presencia_aura" className={classes.labelStyled}>Presencia de aura</label>
                                <select
                                    id="presencia_aura"
                                    name="presencia_aura"
                                    value={formData.presencia_aura}
                                    onChange={handleInputChange}
                                    className={`${classes.selectDefault} ${formData.presencia_aura === '' ? classes.selectPlaceholder : ''}`}
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Sí">Sí</option>
                                    <option value="No">No</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="sintomas_aura" className={classes.labelStyled}>Síntomas del aura</label>
                                <select
                                    id="sintomas_aura"
                                    name="sintomas_aura"
                                    value={formData.sintomas_aura}
                                    onChange={handleInputChange}
                                    className={`${classes.selectDefault} ${formData.sintomas_aura === '' ? classes.selectPlaceholder : ''}`}
                                >
                                    <option value="" disabled>Seleccione una opción</option>
                                    <option value="Ninguno">Ninguno</option>
                                    <option value="Visuales">Visuales</option>
                                    <option value="Sensitivos">Sensitivos</option>
                                    <option value="De habla o lenguaje">De habla o lenguaje</option>
                                    <option value="Motores">Motores</option>
                                    <option value="Troncoencefálicos">Troncoencefálicos</option>
                                    <option value="Retinianos">Retinianos</option>
                                    <option value="Visuales, Sensitivos">Visuales, Sensitivos</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label htmlFor="duracion_aura_minutos" className={classes.labelStyled}>Duración del aura (min)</label>
                                <input
                                    type="number"
                                    id="duracion_aura_minutos"
                                    name="duracion_aura_minutos"
                                    placeholder="Ej: 30"
                                    min="0"
                                    max="120"
                                    value={formData.duracion_aura_minutos}
                                    onChange={handleInputChange}
                                    className={classes.inputDefault}
                                />
                            </div>

                            {/* Campos específicos para mujeres */}
                            {userInfo?.genero === 'F' && (
                                <>
                                    <div className="form-field">
                                        <label htmlFor="en_menstruacion" className={classes.labelStyled}>En menstruación</label>
                                        <select
                                            id="en_menstruacion"
                                            name="en_menstruacion"
                                            value={formData.en_menstruacion}
                                            onChange={handleInputChange}
                                            className={`${classes.selectDefault} ${formData.en_menstruacion === '' ? classes.selectPlaceholder : ''}`}
                                        >
                                            <option value="" disabled>Seleccione una opción</option>
                                            <option value="Sí">Sí</option>
                                            <option value="No">No</option>
                                        </select>
                                    </div>

                                    <div className="form-field">
                                        <label htmlFor="anticonceptivos" className={classes.labelStyled}>Anticonceptivos</label>
                                        <select
                                            id="anticonceptivos"
                                            name="anticonceptivos"
                                            value={formData.anticonceptivos}
                                            onChange={handleInputChange}
                                            className={`${classes.selectDefault} ${formData.anticonceptivos === '' ? classes.selectPlaceholder : ''}`}
                                        >
                                            <option value="" disabled>Seleccione una opción</option>
                                            <option value="Sí">Sí</option>
                                            <option value="No">No</option>
                                        </select>
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="form-buttons">
                            <button type="submit" className={classes.btnPrimary} disabled={loading}>
                                {loading ? 'Guardando...' : 'Registrar'}
                            </button>
                            <button type="button" className={classes.btnCancel} onClick={handleCancel} disabled={loading}>
                                Cancelar
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
