import React, { useState } from "react";
import styles from "../styles/TablaExpandible.module.css"
export default function TablaExpandible({ data = [], keyField = "id" }) {
    const [expandedRow, setExpandedRow] = useState(null);

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

                    return (
                        <React.Fragment key={registro[keyField]}>
                            <tr
                                onClick={() => toggleRow(registro[keyField])}
                            >
                                <td>{registro.fecha_autoevaluacion}</td>
                                <td>{registro.puntaje_total}</td>
                                <td>{registro.grado_discapacidad}</td>
                            </tr>
                            {expandedRow === registro[keyField] && (
                                <tr>
                                    <td className={styles["midas_tabla-resultados"]} colSpan={3}>
                                        <table>
                                            <thead>
                                                <tr>
                                                    <th style={{ textAlign: "left !important" }}>Pregunta</th>
                                                    <th style={{ textAlign: "left !important" }}>Puntaje</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {registro.respuestas_midas_individuales.map((respuesta, i) => (
                                                    <tr key={i}>
                                                        <td style={{ textAlign: "left !important" }}>{respuesta.pregunta.enunciado_pregunta}</td>
                                                        <td style={{ textAlign: "left !important" }}>{respuesta.valor_respuesta}</td>
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
