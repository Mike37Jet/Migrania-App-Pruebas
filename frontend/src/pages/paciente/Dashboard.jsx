import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from "../../common/styles/dashboardPaciente.module.css";
import { BellIcon, StethoscopeIcon, ChartLineIcon, FilesIcon, PillIcon, PlusIcon, BrainIcon } from "@phosphor-icons/react";
import { fetchEpisodiosPaciente } from "../../utils/apiUtils.js";
import {
    obtenerFechaEpisodio,
    compararFechas,
    formatearFecha
} from "../../utils/funciones.js";

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

    const procesarEpisodios = (episodios) => {
        if (!Array.isArray(episodios)) {
            throw new Error('Formato de datos incorrecto recibido de la API');
        }

        return episodios
            .filter(episodio => episodio && obtenerFechaEpisodio(episodio))
            .sort(compararFechas)
            .slice(0, 4);
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

    const handleNavegacion = (ruta) => {
        navigate(ruta);
    };

    const TarjetaDashboard = ({  color, backgroundColor, titulo, descripcion, onClick }) => (
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
                <BellIcon size={32} color="var(--color-text)" />
            </div>

            <section className={styles["dashboard__contenedor-tarjetas"]}>
                <TarjetaDashboard {...TARJETAS_DASHBOARD[0]} onClick={() => handleNavegacion('/bitacora-paciente')} />
                <TarjetaDashboard {...TARJETAS_DASHBOARD[1]} onClick={() => handleNavegacion('/midas')} />
                <TarjetaDashboard {...TARJETAS_DASHBOARD[2]} onClick={() => handleNavegacion('/historialTratamientos')} />
                <TarjetaDashboard {...TARJETAS_DASHBOARD[3]} onClick={() => console.log('Navegando a progreso')} />
                <TarjetaDashboard {...TARJETAS_DASHBOARD[4]} onClick={() =>  handleNavegacion('/analisis-patrones')} />
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
        </>
    );
}
