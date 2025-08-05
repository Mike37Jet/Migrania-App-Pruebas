import styles from "../styles/Midas.module.css";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ModalDisponibilidad from "../components/ModalDisponibilidad";

export default function Midas() {

    const navigate = useNavigate();
    const [indice, setIndice] = useState(0);
    const [preguntas, setPreguntas] = useState([]);
    const [respuestas, setRespuestas] = useState(Array(preguntas.length).fill(""));
    const [valorRespuesta, setValorRespuesta] = useState("");
    const [mostrarModal, setMostrarModal] = useState(true);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPreguntas = async () => {
            try {
                setLoading(true);
                const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjY4MjE0LCJpYXQiOjE3NTQyNjQ2MTQsImp0aSI6IjFkNDk1NWZjN2Y0YjQyYWM5NTg0OWFmNDcxNWVjYTRmIiwidXNlcl9pZCI6Ijk4NSJ9.z43h4CahAjL8dt63WjV5dQ2Sm6sfDgt0-VEfW2Ds-Z0"; // o donde lo tengas guardado

                const response = await fetch('http://localhost:8000/api/evaluaciones/preguntas/', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    }
                });
                const data = await response.json();

                const enunciadosOrdenados = data.results
                    .sort((a, b) => a.orden_pregunta - b.orden_pregunta)
                    .map(p => p.enunciado_pregunta);
                setPreguntas(enunciadosOrdenados);
            } catch (error) {
                console.error('Error al obtener preguntas:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchPreguntas()
        setMostrarModal(true);
    }, []);

    const responderPregunta = () => {
        const nuevasRespuestas = [...respuestas];
        nuevasRespuestas[indice] = valorRespuesta;
        setRespuestas(nuevasRespuestas);
        setValorRespuesta("");

        if (indice < preguntas.length - 1) {
            setIndice(indice + 1);
        } else {
            alert("Respuestas registradas: " + JSON.stringify(nuevasRespuestas));
        }
    };

    return (
        <div className={styles["midas__contenedor"]}>
            {mostrarModal && <ModalDisponibilidad onClose={() => setMostrarModal(false)} />}
            <h1>Autoevaluación MIDAS</h1>
            {loading ? (
                <p>Cargando preguntas...</p>
            ) :
                <div className={styles["midas__tarjeta-pregunta"]}>
                    <h2>Pregunta {indice + 1}</h2>
                    <p>{preguntas[indice]}</p>

                    <p style={{ color: "var(--color-secondary-dark)" }}>Número de días</p>
                    <input
                        type="number"
                        placeholder="Ej: 5"
                        min={0}
                        max={90}
                        value={valorRespuesta}
                        onChange={(e) => setValorRespuesta(e.target.value)}
                    />

                    <div className={styles["midas__contenedor-botones"]}>
                        <button
                            className="btn-secondary"
                            disabled={indice === 0}
                            onClick={() => {
                                const nuevaRespuesta = respuestas[indice - 1] || "";
                                setIndice(indice - 1);
                                setValorRespuesta(nuevaRespuesta);
                            }}
                        >
                            Regresar
                        </button>
                        {
                            indice < preguntas.length - 1 ? (
                                <button
                                    className="btn-primary"
                                    onClick={responderPregunta}
                                    disabled={valorRespuesta === ""}
                                >
                                    Siguiente
                                </button>
                            ) : (
                                <button
                                    className="btn-primary"
                                    onClick={() => {
                                        const nuevasRespuestas = [...respuestas];
                                        nuevasRespuestas[indice] = valorRespuesta;
                                        setRespuestas(nuevasRespuestas);

                                        navigate("/midas/resultados", {
                                            state: {
                                                respuestas: nuevasRespuestas,
                                                preguntas: preguntas
                                            }
                                        });
                                    }}
                                    disabled={valorRespuesta === ""}
                                >
                                    Finalizar
                                </button>

                            )
                        }
                    </div>
                </div>}
        </div>
    );
}
