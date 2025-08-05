import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/historialTratamientos.css"; // asegúrate de importar el CSS correcto

const HistorialTratamientos = () => {
    const navigate = useNavigate();

    const tratamientos = [
        {
            id: 1,
            episodio: 2,
            fecha: "01/08/25",
            estado: "Finalizado",
            cumplimiento: "50%",
            detalle: {
                cantidad: 1,
                medicamento: "Analgésicos",
                caracteristica: "500mg",
                frecuencia: "C/8h",
                duracion: "3 días",
                recomendaciones: [
                    "Mantener una rutina regular de sueño",
                    "Realizar ejercicio de forma moderada"
                ]
            }
        },
        {
            id: 2,
            episodio: 1,
            fecha: "28/07/25",
            estado: "Finalizado",
            cumplimiento: "75%",
            detalle: {
                cantidad: 2,
                medicamento: "Ibuprofeno",
                caracteristica: "400mg",
                frecuencia: "C/6h",
                duracion: "5 días",
                recomendaciones: [
                    "Mantener una hidratación adecuada",
                    "Evitar esfuerzo físico excesivo"
                ]
            }
        }
    ];

    const [modalAbierto, setModalAbierto] = useState(false);
    const [tratamientoSeleccionado, setTratamientoSeleccionado] = useState(null);

    const abrirModal = (tratamiento) => {
        setTratamientoSeleccionado(tratamiento);
        setModalAbierto(true);
    };

    const cerrarModal = () => {
        setModalAbierto(false);
        setTratamientoSeleccionado(null);
    };

    return (
        <div className="historial-container">
            <h1>Paciente X - Historial de Tratamientos</h1>
            <div className="historial-header">
                <button className="historial-back-button" onClick={() => navigate(-1)}>Regresar</button>
            </div>

            <table className="historial-table">
                <thead>
                <tr>
                    <th># Tratamiento</th>
                    <th>Episodio</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                    <th>% Cumplimiento</th>
                    <th>Acciones</th>
                </tr>
                </thead>
                <tbody>
                {tratamientos.map((t) => (
                    <tr key={t.id}>
                        <td>{t.id}</td>
                        <td>{t.episodio}</td>
                        <td>{t.fecha}</td>
                        <td>{t.estado}</td>
                        <td>{t.cumplimiento}</td>
                        <td>
                            <button className="historial-ver-button" onClick={() => abrirModal(t)}>Ver</button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>

            {modalAbierto && tratamientoSeleccionado && (
                <div className="ver-modal">
                    <div className="ver-modal-content">
                        <h2>Tratamiento #{tratamientoSeleccionado.id}</h2>
                        <table>
                            <thead>
                            <tr>
                                <th>Cantidad</th>
                                <th>Medicamento</th>
                                <th>Característica</th>
                                <th>Frecuencia</th>
                                <th>Duración Tratamiento</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <td>{tratamientoSeleccionado.detalle.cantidad}</td>
                                <td>{tratamientoSeleccionado.detalle.medicamento}</td>
                                <td>{tratamientoSeleccionado.detalle.caracteristica}</td>
                                <td>{tratamientoSeleccionado.detalle.frecuencia}</td>
                                <td>{tratamientoSeleccionado.detalle.duracion}</td>
                            </tr>
                            </tbody>
                        </table>
                        <div className="recomendaciones">
                            <h3>Recomendaciones</h3>
                            <ul>
                                {tratamientoSeleccionado.detalle.recomendaciones.map((rec, i) => (
                                    <li key={i}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                        <button className="aceptar" onClick={cerrarModal}>Aceptar</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HistorialTratamientos;
