import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from "../../common/styles/dashboardPaciente.module.css";
import { BellIcon, StethoscopeIcon, ChartLineIcon, FilesIcon, PillIcon, PlusIcon, BrainIcon, AlarmIcon, LightbulbFilamentIcon, SirenIcon } from "@phosphor-icons/react";
import { fetchEpisodiosPaciente } from "../../utils/apiUtils.js";
import {
    obtenerFechaEpisodio,
    compararFechas,
    formatearFecha
} from "../../utils/funciones.js";
import BotonNotificacion from "../../features/feature_Grupo3_Recordatorios/components/notificationPanel/BotonNotificacion";
import ModalNotificaciones from "../../features/feature_Grupo3_Recordatorios/components/notificationPanel/ModalNotificaciones";
import AlertaPopup from "../../features/feature_Grupo3_Recordatorios/components/notification/AlertaPopup";
import RecordatorioPopup from "../../features/feature_Grupo3_Recordatorios/components/notification/RecordatorioPopup";
import NotificacionesService from "../../features/feature_Grupo3_Recordatorios/services/notificacionesService";
import useDetectorNotificacionesEmergentes from "../../features/feature_Grupo3_Recordatorios/hooks/useDetectorNotificacionesEmergentes";
// ...eliminada importación de BotonTestingSimple...

const TARJETAS_DASHBOARD = [
    {
        icono: PlusIcon,
        color: "#c9525aff",
        backgroundColor: "#c42d3750",
        titulo: "Bitácora",
        descripcion: "Mira y registra un nuevo episodio de migraña."
    },
    {
        icono: FilesIcon,
        color: "#a555ebff",
        backgroundColor: "#9f58dd59",
        titulo: "Evaluación MIDAS",
        descripcion: "Evalúa el impacto de la migraña en tu vida diaria."
    },
    {
        icono: PillIcon,
        color: "#4c84f3ff",
        backgroundColor: "#3e68be50",
        titulo: "Mis tratamientos",
        descripcion: "Revisa tus tratamientos actuales."
    },
    {
        icono: ChartLineIcon,
        color: "#42b668ff",
        backgroundColor: "#3588517d",
        titulo: "Mi progreso",
        descripcion: "Visualiza tendencias y estadísticas."
    },
    {
        icono: BrainIcon,
        color: "#f39a4cff",
        backgroundColor: "#be713e50",
        titulo: "Mis patrones",
        descripcion: "Revisa tus patrones semanales."
    }
];

export default function Dashboard() {
    const navigate = useNavigate();
    const [episodiosRecientes, setEpisodiosRecientes] = useState([]);
    const [cargandoEpisodios, setCargandoEpisodios] = useState(true);
    const [errorEpisodios, setErrorEpisodios] = useState(null);
    
    // Estados para las notificaciones
    const [modalNotificacionesAbierto, setModalNotificacionesAbierto] = useState(false);
    const [alertaPopupAbierto, setAlertaPopupAbierto] = useState(false);
    const [recordatorioPopupAbierto, setRecordatorioPopupAbierto] = useState(false);
    const [tieneNotificaciones, setTieneNotificaciones] = useState(false);
    const [contadorNotificaciones, setContadorNotificaciones] = useState(0);
    const [notificaciones, setNotificaciones] = useState([]);
    const [tratamientoId] = useState(6); // ID del tratamiento actual
    // Estado global para controlar el sonido de notificaciones
    const [modoSonido, setModoSonido] = useState("sonido"); // "sonido", "silencio", "suspender"

    // Hook para detectar notificaciones emergentes automáticamente
    const {
        alertaActual: alertaActiva,
        recordatorioActual: recordatorioActivo,
        mostrarAlerta,
        mostrarRecordatorio,
        handleConfirmarAlerta: confirmarAlertaEmergente,
        handleCancelarAlerta: rechazarAlertaEmergente,
        handleDesactivarRecordatorio: cerrarRecordatorioEmergente,
        verificarNotificaciones: verificarNotificacionesPendientes
    } = useDetectorNotificacionesEmergentes(); // Sin parámetros

    const procesarEpisodios = (episodios) => {
        if (!Array.isArray(episodios)) {
            throw new Error('Formato de datos incorrecto recibido de la API');
        }

        return episodios
            .filter(episodio => episodio && obtenerFechaEpisodio(episodio))
            .sort(compararFechas)
            .slice(0, 4);
    };

    // Función para obtener el icono según el tipo
    const obtenerIcono = (tipo) => {
        switch (tipo) {
            case 'medicacion':
                return <AlarmIcon size={32} color="#bad8ecff" weight="fill" />;
            case 'recordatorio':
                return <LightbulbFilamentIcon size={32} color="#f5e400ff" weight="fill" />;
            case 'alerta':
                return <SirenIcon size={32} color="#AA4D53" weight="fill" />;
            default:
                return <AlarmIcon size={32} color="#bad8ecff" weight="fill" />;
        }
    };

    // Función para cargar el contador de notificaciones solo desde el frontend (popups mostrados)
    const cargarNotificaciones = () => {
        // Solo contar las notificaciones emergentes activas
        let contadorEmergentes = 0;
        if (alertaActiva) contadorEmergentes++;
        if (recordatorioActivo) contadorEmergentes++;
        setContadorNotificaciones(contadorEmergentes);
        setTieneNotificaciones(contadorEmergentes > 0);
    };

    useEffect(() => {
        const cargarEpisodiosRecientes = async () => {
            try {
                setCargandoEpisodios(true);
                setErrorEpisodios(null);

                const episodios = await fetchEpisodiosPaciente();
                const episodiosOrdenados = procesarEpisodios(episodios);
                setEpisodiosRecientes(episodiosOrdenados);
            } catch (error) {
                console.error('Error al cargar episodios recientes:', error);
                setErrorEpisodios(error.message);
            } finally {
                setCargandoEpisodios(false);
            }
        };

        cargarEpisodiosRecientes();
    }, []);

    useEffect(() => {
        // Cargar notificaciones al montar el componente y cuando cambien las emergentes
        cargarNotificaciones();
    }, [tratamientoId, alertaActiva, recordatorioActivo]);

    const handleNavegacion = (ruta) => {
        navigate(ruta);
    };

    const handleNavegacionMidas = async () => {

        const token = localStorage.getItem("access");

        try {
            const response = await fetch("http://localhost:8000/api/evaluaciones/autoevaluaciones/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({}),
            });
            const data = await response.json();
            if (!response.ok) {
                if (data.detail === "Debes esperar al menos 90 días para una nueva autoevaluación.") {
                    alert(data.detail);
                    return;
                }

                console.error("Error inesperado:", data);
                return;
            }
            const idAutoevaluacion = data.id;
            navigate("/midas", {
                state: {
                    idAutoevaluacion: idAutoevaluacion
                }
            });

        } catch (error) {
            console.error("Error en la petición:", error);
        }
    };

    // Funciones para manejar las notificaciones
    const handleAbrirModalNotificaciones = () => {
        setModalNotificacionesAbierto(true);
    };

    const handleCerrarModalNotificaciones = () => {
        setModalNotificacionesAbierto(false);
        // Recargar notificaciones cuando se cierre el modal por si se procesaron notificaciones
        cargarNotificaciones();
        // También forzar verificación de notificaciones emergentes
        verificarNotificacionesPendientes();
    };

    // Función específica para manejar la limpieza del modal (solo frontend)
    const handleLimpiarModalNotificaciones = () => {
        // Solo actualizar el contador y estado de notificaciones del modal
        // Los popups emergentes siguen independientes
        setContadorNotificaciones(prev => {
            // Mantener el conteo de emergentes activas
            let contadorEmergentes = 0;
            if (alertaActiva) contadorEmergentes++;
            if (recordatorioActivo) contadorEmergentes++;
            return contadorEmergentes;
        });
        
        setTieneNotificaciones(prev => {
            // Hay notificaciones si hay emergentes activas
            return !!(alertaActiva || recordatorioActivo);
        });

        if (process.env.NODE_ENV === 'development') {
            console.log('Modal de notificaciones limpiado (solo frontend)');
        }
    };

    const handleConfirmarAlerta = () => {
        setAlertaPopupAbierto(false);
        if (process.env.NODE_ENV === 'development') {
            console.log('Alerta confirmada');
        }
        // Recargar notificaciones después de confirmar alerta
        cargarNotificaciones();
    };

    const handleCancelarAlerta = () => {
        setAlertaPopupAbierto(false);
        if (process.env.NODE_ENV === 'development') {
            console.log('Alerta cancelada');
        }
    };

    const handleCerrarRecordatorio = () => {
        setRecordatorioPopupAbierto(false);
        if (process.env.NODE_ENV === 'development') {
            console.log('Recordatorio cerrado');
        }
        // Recargar notificaciones después de cerrar recordatorio
        cargarNotificaciones();
    };

    const TarjetaDashboard = ({ icono: Icono, color, backgroundColor, titulo, descripcion, onClick }) => (
        <div
            className={styles["dashboard__tarjeta"]}
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            <div className={styles["dashboard__icono"]} style={{ backgroundColor }}>
                <Icono size={32} color={color} />
            </div>
            <h4>{titulo}</h4>
            <p>{descripcion}</p>
        </div>
    );

    const EstadoCarga = ({ cargando, error, vacio, textoVacio = "No hay datos disponibles" }) => {
        if (cargando) {
            return <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-secondary-dark)' }}>Cargando...</div>;
        }

        if (error) {
            return <div style={{ textAlign: 'center', padding: '20px', color: '#e74c3c' }}>Error: {error}</div>;
        }

        if (vacio) {
            return <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-secondary-dark)' }}>{textoVacio}</div>;
        }

        return null;
    };

    const DetalleEpisodio = ({ icono, texto }) => (
        <div className={styles["dashboard__episodio-detalle"]}>
            <div className={styles["dashboard__episodio-detalle-icono"]}>{icono}</div>
            <span className={styles["dashboard__episodio-detalle-texto"]}>{texto}</span>
        </div>
    );

    const EpisodioItem = ({ episodio, index }) => {
        const fechaFormateada = formatearFecha(obtenerFechaEpisodio(episodio));
        const severidadClass = episodio.severidad
            ? styles[`dashboard__episodio-severidad--${episodio.severidad.toLowerCase()}`]
            : '';

        return (
            <div key={episodio.id || index} className={styles["dashboard__episodio-item"]}>
                <div className={styles["dashboard__episodio-fecha"]}>{fechaFormateada}</div>
                <div className={styles["dashboard__episodio-contenido"]}>
                    <div className={styles["dashboard__episodio-header"]}>
                        <div className={`${styles["dashboard__episodio-severidad"]} ${severidadClass}`}>
                            {episodio.severidad || 'N/A'}
                        </div>
                    </div>
                    <div className={styles["dashboard__episodio-detalles"]}>
                        <DetalleEpisodio icono="⏱" texto={episodio.duracion_cefalea_horas || episodio.duracion || 'N/A'} />
                        {episodio.localizacion && <DetalleEpisodio icono="📍" texto={episodio.localizacion} />}
                        {(episodio.caracter_dolor || episodio.desencadenante) && (
                            <DetalleEpisodio icono="💫" texto={episodio.caracter_dolor || episodio.desencadenante} />
                        )}
                    </div>
                </div>
            </div>
        );
    };

    return (
        <>
            <div className={styles["dashboard__cabecera"]}>
                <div>
                    <h2>¿Cómo te sientes hoy?</h2>
                    <p>¡Vas 5 días sin episodios! Sigue cuidándote y registrando tus síntomas.</p>
                </div>
                <BotonNotificacion 
                    onClick={handleAbrirModalNotificaciones}
                    hasNotifications={tieneNotificaciones}
                    notificationCount={contadorNotificaciones}
                />
            </div>

            <section className={styles["dashboard__contenedor-tarjetas"]}>
                <TarjetaDashboard {...TARJETAS_DASHBOARD[0]} onClick={() => handleNavegacion('/bitacora-paciente')} />

                <TarjetaDashboard {...TARJETAS_DASHBOARD[1]} onClick={() => handleNavegacionMidas()} />
                <TarjetaDashboard {...TARJETAS_DASHBOARD[2]} onClick={() => console.log('Navegando a tratamientos')} />

                <TarjetaDashboard {...TARJETAS_DASHBOARD[3]} onClick={() => console.log('Navegando a progreso')} />
                <TarjetaDashboard {...TARJETAS_DASHBOARD[4]} onClick={() => handleNavegacion('/analisis-patrones')} />
            </section>

            <div className={styles["dashboard__seccion-inferior"]}>
                <section className={styles["dashboard__episodios-recientes"]}>
                    <h4>Episodios recientes</h4>

                    <EstadoCarga
                        cargando={cargandoEpisodios}
                        error={errorEpisodios}
                        vacio={episodiosRecientes.length === 0}
                        textoVacio="No hay episodios registrados"
                    />

                    {!cargandoEpisodios && !errorEpisodios && episodiosRecientes.length > 0 && (
                        <div className={styles["dashboard__lista-episodios"]}>
                            {episodiosRecientes.map((episodio, index) => (
                                <EpisodioItem key={episodio.id || index} episodio={episodio} index={index} />
                            ))}
                        </div>
                    )}
                </section>

                <section className={styles["dashboard__mi-medico"]}>
                    <h4>Mi médico</h4>

                    <div className={styles["dashboard__medico-info"]}>
                        <StethoscopeIcon size={64} />
                        <h4>Dr. Juan Pérez</h4>
                        <p>Especialista en Neurología</p>
                    </div>

                    <div>
                        <h4>Próxima cita:</h4>
                        <div style={{ color: "var(--color-secondary-dark)" }}>2025-10-22 - 10:00 AM</div>
                    </div>

                    <div>
                        <h4>Tratamiento actual:</h4>
                        <div style={{ color: "var(--color-secondary-dark)" }}>Propranolol 40mg</div>
                    </div>

                    <button className="btn-primary">Agendar</button>
                </section>
            </div>

            {/* Componentes de notificaciones */}
            <ModalNotificaciones 
                isOpen={modalNotificacionesAbierto}
                onClose={handleCerrarModalNotificaciones}
                tratamientoId={tratamientoId}
                notificacionesExternas={notificaciones}
                onNotificacionesChange={handleLimpiarModalNotificaciones}
                modoSonido={modoSonido}
                setModoSonido={setModoSonido}
            />

            {/* 
              Popups emergentes automáticos - INDEPENDIENTES del modal
              - Aparecen cuando el backend tiene notificaciones con estado SIN_CONFIRMAR/ACTIVO
              - Tienen sus propios botones para desactivar en el backend
              - No se ven afectados por el botón "Borrar todo" del modal
            */}

            {modoSonido !== "suspender" && (
                <AlertaPopup 
                    isOpen={mostrarAlerta && !!alertaActiva}
                    onConfirm={confirmarAlertaEmergente}
                    onCancel={rechazarAlertaEmergente}
                    mensaje={alertaActiva?.mensaje || "Confirma si has tomado tu medicamento según lo prescrito"}
                    fecha_hora={alertaActiva?.fecha_hora || null}
                    alertaId={alertaActiva?.id}
                    modoSonido={modoSonido}
                />
            )}

            {modoSonido !== "suspender" && (
                <RecordatorioPopup 
                    isOpen={mostrarRecordatorio && !!recordatorioActivo}
                    onClose={cerrarRecordatorioEmergente}
                    type={recordatorioActivo?.tipo || "medicina"}
                    mensaje={recordatorioActivo?.mensaje || "Recuerda tomar tu medicamento según las indicaciones médicas"}
                    fecha_hora={recordatorioActivo?.fecha_hora || null}
                    recordatorioId={recordatorioActivo?.id}
                    modoSonido={modoSonido}
                />
            )}

            {/* Popups manuales (para casos específicos si es necesario) */}
            {modoSonido !== "suspender" && (
                <AlertaPopup 
                    isOpen={alertaPopupAbierto}
                    onConfirm={handleConfirmarAlerta}
                    onCancel={handleCancelarAlerta}
                    title="¿Tomaste la medicación?"
                    message="Confirma si has tomado tu medicamento según lo prescrito"
                    modoSonido={modoSonido}
                    horaMedicacion={null}
                />
            )}

            {modoSonido !== "suspender" && (
                <RecordatorioPopup 
                    isOpen={recordatorioPopupAbierto}
                    onClose={handleCerrarRecordatorio}
                    type="medicina"
                    message="Recuerda tomar tu medicamento según las indicaciones médicas"
                    modoSonido={modoSonido}
                />
            )}

            {/* Botón de testing para simular notificaciones */}
            {/* ...eliminado BotonTestingSimple... */}
        </>
    );
}
