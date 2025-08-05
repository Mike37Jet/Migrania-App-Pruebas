import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeSlash, ArrowLeft } from '@phosphor-icons/react';
import styles from '../styles/Registro.module.css';

export default function Registro() {
    const [nombre, setNombre] = useState('');
    const [apellido, setApellido] = useState('');
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rol, setRol] = useState('');
    const [cedula, setCedula] = useState('');
    
    // Campos para paciente
    const [contactoEmergenciaNombre, setContactoEmergenciaNombre] = useState('');
    const [contactoEmergenciaRelacion, setContactoEmergenciaRelacion] = useState('');
    const [contactoEmergenciaTelefono, setContactoEmergenciaTelefono] = useState('');
    
    // Campos para médico
    const [anosExperiencia, setAnosExperiencia] = useState('');
    const [especializacion, setEspecializacion] = useState('');
    const [numeroLicencia, setNumeroLicencia] = useState('');
    
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // Determinar la URL según el rol
            const apiUrl = rol === 'medico' 
                ? 'http://localhost:8000/api/registro-medico/'
                : 'http://localhost:8000/api/registro-paciente/';

            // Datos base comunes
            let userData = {
                nombre,
                apellido,
                username,
                email,
                password
            };

            // Agregar campos específicos según el rol
            if (rol === 'paciente') {
                userData = {
                    ...userData,
                    contacto_emergencia_nombre: contactoEmergenciaNombre,
                    contacto_emergencia_relacion: contactoEmergenciaRelacion,
                    contacto_emergencia_telefono: contactoEmergenciaTelefono,
                    cedula
                };
            } else if (rol === 'medico') {
                userData = {
                    ...userData,
                    anos_experiencia: parseInt(anosExperiencia),
                    especializacion,
                    numero_licencia: numeroLicencia,
                    cedula 
                };
            }

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Registro exitoso:', data);
                
                // Redirigir al login o mostrar mensaje de éxito
                navigate('/login', { 
                    state: { 
                        message: 'Registro exitoso. Por favor, inicia sesión.' 
                    } 
                });
            } else {
                const errorData = await response.json();
                console.log('Error del servidor:', errorData);
                
                // Extraer mensajes de error específicos
                let errorMessage = 'Error en el registro. Inténtalo de nuevo.';
                if (errorData.errors) {
                    const errorMessages = Object.entries(errorData.errors)
                        .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
                        .join('; ');
                    errorMessage = errorMessages;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
                
                setError(errorMessage);
            }
        } catch (error) {
            console.error('Error al registrar:', error);
            setError('Error de conexión. Verifica tu conexión a internet.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleGoBack = () => {
        navigate('/login');
    };

    return (
        <div className={styles["registro"]}>
            <div className={styles["registro__tarjeta"]}>
                <button 
                    type="button" 
                    onClick={handleGoBack}
                    className={styles["registro__boton-volver"]}
                >
                    <ArrowLeft size={32} />
                </button>
                
                <h1 className={styles.registro__titulo}>Regístrate</h1>

                <form onSubmit={handleSubmit} className={styles["registro__formulario"]}>
                    {error && (
                        <div className={styles["registro__mensaje-error"]}>
                            {error}
                        </div>
                    )}

                    <div className={styles["registro__grupo-input"]}>
                        <label htmlFor="rol">Tipo de usuario</label>
                        <select
                            id="rol"
                            value={rol}
                            onChange={(e) => setRol(e.target.value)}
                            className={styles["registro__select"]}
                            required
                            disabled={isLoading}
                        >
                            <option value="">Selecciona tu rol</option>
                            <option value="paciente">Paciente</option>
                            <option value="medico">Médico</option>
                        </select>
                    </div>

                    <div className={styles["registro__grupo-input"]}>
                        <label htmlFor="username">Nombre de usuario</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Nombre de usuario único"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className={styles["registro__grupo-input"]}>
                        <label htmlFor="nombre">Nombre</label>
                        <input
                            type="text"
                            id="nombre"
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value)}
                            placeholder="Nombre"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className={styles["registro__grupo-input"]}>
                        <label htmlFor="apellido">Apellido</label>
                        <input
                            type="text"
                            id="apellido"
                            value={apellido}
                            onChange={(e) => setApellido(e.target.value)}
                            placeholder="Apellido"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className={styles["registro__grupo-input"]}>
                        <label htmlFor="email">Dirección de correo electrónico</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Por ejemplo: john@company.com"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className={styles["registro__grupo-input"]}>
                        <label htmlFor="password">Contraseña</label>
                        <div className={styles["registro__contenedor-password"]}>
                            <input
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Más de 12 caracteres"
                                required
                                disabled={isLoading}
                            />
                            <span
                                className={styles["registro__icono-password"]}
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeSlash size={22} /> : <Eye size={22} />}
                            </span>
                        </div>
                    </div>


                    {rol === 'paciente' && (
                        <>
                            <h3 style={{ color: 'var(--color-text)', margin: '0', fontSize: 'var(--font-size-m)' }}>
                                Información del Paciente
                            </h3>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="cedula">Cédula</label>
                                <input
                                    type="text"
                                    id="cedula"
                                    value={cedula}
                                    onChange={(e) => setCedula(e.target.value)}
                                    placeholder="Número de cédula"
                                    required
                                    disabled={isLoading}
                                />
                            </div>

                            <h3 style={{ color: 'var(--color-text)', margin: '0', fontSize: 'var(--font-size-m)' }}>
                                Contacto de Emergencia
                            </h3>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="contactoEmergenciaNombre">Nombre del contacto</label>
                                <input
                                    type="text"
                                    id="contactoEmergenciaNombre"
                                    value={contactoEmergenciaNombre}
                                    onChange={(e) => setContactoEmergenciaNombre(e.target.value)}
                                    placeholder="Nombre completo"
                                    required
                                    disabled={isLoading}
                                />
                            </div>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="contactoEmergenciaRelacion">Relación</label>
                                <select
                                    id="contactoEmergenciaRelacion"
                                    value={contactoEmergenciaRelacion}
                                    onChange={(e) => setContactoEmergenciaRelacion(e.target.value)}
                                    className={styles["registro__select"]}
                                    required
                                    disabled={isLoading}
                                >
                                    <option value="">Selecciona la relación</option>
                                    <option value="padre">Padre</option>
                                    <option value="madre">Madre</option>
                                    <option value="hermano">Hermano/a</option>
                                    <option value="conyuge">Cónyuge</option>
                                    <option value="hijo">Hijo/a</option>
                                    <option value="amigo">Amigo/a</option>
                                    <option value="otro">Otro</option>
                                </select>
                            </div>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="contactoEmergenciaTelefono">Teléfono</label>
                                <input
                                    type="tel"
                                    id="contactoEmergenciaTelefono"
                                    value={contactoEmergenciaTelefono}
                                    onChange={(e) => setContactoEmergenciaTelefono(e.target.value)}
                                    placeholder="Número de teléfono"
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                        </>
                    )}

                    {/* Campos específicos para MÉDICO */}
                    {rol === 'medico' && (
                        <>
                            <h3 style={{ color: 'var(--color-text)', margin: '0', fontSize: 'var(--font-size-m)' }}>
                                Información Personal
                            </h3>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="cedula">Cédula</label>
                                <input
                                    type="text"
                                    id="cedula"
                                    value={cedula}
                                    onChange={(e) => setCedula(e.target.value)}
                                    placeholder="Número de cédula"
                                    required
                                    disabled={isLoading}
                                />
                            </div>

                            <h3 style={{ color: 'var(--color-text)', margin: '0', fontSize: 'var(--font-size-m)' }}>
                                Información Profesional
                            </h3>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="numeroLicencia">Número de Licencia</label>
                                <input
                                    type="text"
                                    id="numeroLicencia"
                                    value={numeroLicencia}
                                    onChange={(e) => setNumeroLicencia(e.target.value)}
                                    placeholder="Número de licencia médica"
                                    required
                                    disabled={isLoading}
                                />
                            </div>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="especializacion">Especialización</label>
                                <input
                                    type="text"
                                    id="especializacion"
                                    value={especializacion}
                                    onChange={(e) => setEspecializacion(e.target.value)}
                                    placeholder="Especialidad médica"
                                    required
                                    disabled={isLoading}
                                />
                            </div>

                            <div className={styles["registro__grupo-input"]}>
                                <label htmlFor="anosExperiencia">Años de Experiencia</label>
                                <input
                                    type="number"
                                    id="anosExperiencia"
                                    value={anosExperiencia}
                                    onChange={(e) => setAnosExperiencia(e.target.value)}
                                    placeholder="Años de experiencia"
                                    min="0"
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                        </>
                    )}

                    <button 
                        type="submit" 
                        className={styles["registro__boton"]}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Registrando...' : 'Registrarse'}
                    </button>
                </form>
            </div>
        </div>
    );
}