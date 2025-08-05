import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TarjetaResumen from '../components/TarjetaResumen';
import TarjetaAnalisis from '../components/TarjetaAnalisis';
import styles from '../styles/AnalisisPatrones.module.css';
import { ArrowLeft, ChartLineUp, Warning, Drop, Calendar } from '@phosphor-icons/react';

const EstadoCarga = ({ cargando, error, children }) => {
    if (cargando) {
        return <p style={{ textAlign: 'center', color: 'var(--color-text-muted)' }}>Cargando análisis de patrones...</p>;
    }
    if (error) {
        return <p style={{ textAlign: 'center', color: 'var(--color-error)' }}>Error: {error}</p>;
    }
    return children;
};

export default function AnalisisPatrones() {
    const navigate = useNavigate();
    const [patronesData, setPatronesData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPatrones = async () => {
            const token = localStorage.getItem("access");
            if (!token) {
                setError("No autenticado. Por favor, inicie sesión.");
                setIsLoading(false);
                return;
            }
            try {
                const response = await fetch("http://127.0.0.1:8000/api/analiticas/patrones/", {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (!response.ok) throw new Error(`Error: ${response.status}`);
                const data = await response.json();
                setPatronesData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchPatrones();
    }, []);

    const handleVolver = () => navigate(-1);

    const tarjetasDeAnalisis = [];
    if (patronesData) {
        if (patronesData.conclusion_clinica) {
            tarjetasDeAnalisis.push({
                id: 'clinica',
                icono: <Warning size={32} />,
                titulo: "Factores Médicos",
                descripcion: patronesData.conclusion_clinica,
                recomendacion: "Considera consultar a un profesional de salud para una evaluación médica."
            });
        }
        if (patronesData.conclusiones_sintomas?.sintoma_frecuente) {
            tarjetasDeAnalisis.push({
                id: 'sintomas',
                icono: <Warning size={32} />,
                titulo: "Síntoma Frecuente",
                descripcion: patronesData.conclusiones_sintomas.sintoma_frecuente,
                recomendacion: "Presta atención a este síntoma, ya que es recurrente en tus episodios."
            });
        }
        if (patronesData.conclusion_aura) {
            tarjetasDeAnalisis.push({
                id: 'aura',
                icono: <ChartLineUp size={32} />,
                titulo: "Análisis de Aura",
                descripcion: patronesData.conclusion_aura,
                recomendacion: "El registro de auras es importante para un diagnóstico preciso."
            });
        }
        if (patronesData.dias_recurrentes?.length > 0) {
            
            const dias = patronesData.dias_recurrentes.join(', ');
            tarjetasDeAnalisis.push({
                id: 'recurrencia',
                icono: <Calendar size={32} />,
                titulo: "Recurrencia Semanal",
                descripcion: `Se ha detectado un aumento de episodios los días: ${dias}.`,
                recomendacion: "Evalúa tu rutina en estos días para identificar posibles desencadenantes."
            });
        }
        if (patronesData.conclusion_hormonal) {
            tarjetasDeAnalisis.push({
                id: 'hormonal',
                icono: <Drop size={32} />,
                titulo: "Patrón Hormonal",
                descripcion: patronesData.conclusion_hormonal,
                recomendacion: "Si sospechas de migraña menstrual, coméntalo con tu médico."
            });
        }
    }

    return (
        <div className={styles.patrones}> 
            <header className={styles.patrones__cabecera}>
                <button onClick={handleVolver} className={styles.patrones__botonVolver}>
                    <ArrowLeft size={24} />
                    Volver
                </button>
            </header>

            <section className={styles.patrones__resumen}>
                <TarjetaResumen
                    titulo="Patrones Identificados"
                    valor={tarjetasDeAnalisis.length} 
                    subtitulo="Basado en tus registros"
                    icono={<ChartLineUp size={48} weight="light" />}
                    color="secondary-light"
                />
                <TarjetaResumen
                    titulo="Alertas Preventivas"
                    valor={tarjetasDeAnalisis.filter(t => t.id !== 'aura').length} 
                    subtitulo="Patrones detectados"
                    icono={<Warning size={48} weight="light" />}
                    color="secondary-dark"
                    iconColor="var(--color-error)"
                />
            </section>

            <section className={styles.patrones__analisis}>
                <EstadoCarga cargando={isLoading} error={error}>
                    {tarjetasDeAnalisis.length > 0 ? (
                        tarjetasDeAnalisis.map(tarjeta => (
                            <TarjetaAnalisis
                                key={tarjeta.id}
                                icono={tarjeta.icono}
                                titulo={tarjeta.titulo}
                                descripcion={tarjeta.descripcion}
                                recomendacion={tarjeta.recomendacion}
                            />
                        ))
                    ) : (
                        <p>No se han encontrado patrones significativos. ¡Sigue registrando tus episodios!</p>
                    )}
                </EstadoCarga>
            </section>
        </div>
    );
}