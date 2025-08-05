import midasStyles from "../styles/Midas.module.css";
import styles from "../styles/Resultados.module.css";
import { useLocation, useNavigate } from "react-router-dom";

function ResultadosRow({ pregunta, puntuacion }) {
    return (
        <div className={styles["resultados__resultado"]}>
            <span>{pregunta}</span>
            <span>{puntuacion}</span>
        </div>
    );
}

export default function Resultados() {
    const location = useLocation();
    const navigate = useNavigate();
    const respuestas = location.state?.respuestas || [];
    const preguntas = location.state?.preguntas || [];
    const puntuacionTotal = respuestas.reduce((sum, val) => sum + Number(val || 0), 0);

    // Mensaje según la puntuación total
    const interpretarPuntuacion = (puntaje) => {
        if (puntaje <= 5) return "Discapacidad mínima.";
        if (puntaje <= 10) return "Discapacidad leve. Se recomienda observación.";
        if (puntaje <= 20) return "Discapacidad moderada. Se recomienda evaluación médica.";
        return "Discapacidad grave. Se recomienda tratamiento especializado.";
    };

    return (
        <div className={midasStyles["midas__contenedor"]}>
            <div className={styles["resultados__tarjeta-resultados"]}>
                <div className={styles["resultados__seccion-superior"]}>
                    <h1>Resultados</h1>
                    <h4>Puntuación: {puntuacionTotal}</h4>
                    <p>{interpretarPuntuacion(puntuacionTotal)}</p>
                </div>

                <div className={styles["resultados__seccion-inferior"]}>
                    <h3>Tus respuestas</h3>
                    <div className={styles["resultados__lista"]}>
                        <div>
                            {preguntas.slice(0, 3).map((pregunta, i) => (
                                <ResultadosRow
                                    key={i}
                                    pregunta={pregunta}
                                    puntuacion={respuestas[i] || 0}
                                />
                            ))}
                        </div>
                        <div>
                            {preguntas.slice(3).map((pregunta, i) => (
                                <ResultadosRow
                                    key={i + 3}
                                    pregunta={pregunta}
                                    puntuacion={respuestas[i + 3] || 0}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                <div className={styles["resultados__boton-inferior"]}>
                    <button className="btn-primary" onClick={() => navigate("/dashboard-paciente")}>
                        ¡Listo!
                    </button>
                </div>
            </div>
        </div>
    );
}
