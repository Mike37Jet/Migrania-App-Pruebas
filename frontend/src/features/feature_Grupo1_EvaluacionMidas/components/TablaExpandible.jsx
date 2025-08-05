import React, { useState } from "react";
import styles from "../styles/TablaExpandible.module.css"
export default function TablaExpandible({ data = [], keyField = "id" }) {
    const [expandedRow, setExpandedRow] = useState(null);

    const preguntas = [
        "¿Cuántos días en los últimos 3 meses faltaste al trabajo o a la escuela debido a tus dolores de cabeza?",
        "¿Cuántos días en los últimos 3 meses redujiste tu productividad a la mitad o menos en el trabajo o la escuela?",
        "¿Cuántos días no realizaste tareas del hogar debido a los dolores de cabeza?",
        "¿Cuántos días tuviste que reducir a la mitad o más tu rendimiento en tareas del hogar?",
        "¿Cuántos días evitaste actividades sociales o familiares por dolores de cabeza?",
    ];

    const toggleRow = (id) => {
        setExpandedRow(expandedRow === id ? null : id);
    };

    return (
        <table>
            <thead>
                <tr>
                    <th>Fecha de Evaluación</th>
                    <th>Puntaje Total</th>
                    <th>Grado de Discapacidad</th>
                </tr>
            </thead>
            <tbody>
                {data.map((registro) => {
                    const puntajeTotal = registro.respuestas.reduce(
                        (acc, val) => acc + Number(val || 0),
                        0
                    );

                    const gradoDiscapacidad = () => {
                        if (puntajeTotal <= 5) return "Mínima";
                        if (puntajeTotal <= 10) return "Leve";
                        if (puntajeTotal <= 20) return "Moderada";
                        return "Grave";
                    };

                    return (
                        <React.Fragment key={registro[keyField]}>
                            <tr
                                onClick={() => toggleRow(registro[keyField])}
                            >
                                <td>{registro.fechaEvaluacion}</td>
                                <td>{puntajeTotal}</td>
                                <td>{gradoDiscapacidad()}</td>
                            </tr>
                            {expandedRow === registro[keyField] && (
                                <tr>
                                    <td className={styles["midas_tabla-resultados"]} colSpan={3}>
                                        <table>
                                            <thead>
                                                <tr>
                                                    <th style={{textAlign: "left !important"}}>Pregunta</th>
                                                    <th style={{textAlign: "left !important"}}>Puntaje</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {registro.respuestas.map((puntaje, i) => (
                                                    <tr key={i}>
                                                        <td style={{textAlign: "left !important"}}>{preguntas[i]}</td>
                                                        <td style={{textAlign: "left !important"}}>{puntaje}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            )}
                        </React.Fragment>
                    );
                })}
            </tbody>
        </table>
    );
}
