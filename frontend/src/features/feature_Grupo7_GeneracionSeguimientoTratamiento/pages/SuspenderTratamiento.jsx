import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/suspenderTratamiento.css";

function SuspenderTratamiento() {
    const [mostrarModal, setMostrarModal] = useState(false);
    const navigate = useNavigate();
    const suspender = () => {
        setMostrarModal(true); // muestra el modal
    };

    const aceptar = () => {
        setMostrarModal(false);
        navigate("/home");
    };
    const tratamientoActivo = {
        cantidad: 1,
        medicamento: "Analgésicos",
        caracteristica: "500mg",
        frecuencia: "C/8horas",
        duracion: "3 días",
        cumplimiento: "15%",
    };

    return (
        <div className="suspender-tratamiento">
            <header>
                <div className="user-info">
                    <span className="user-icon">👤</span>
                    <span className="user-name">Dr. X</span>
                </div>
            </header>

            <h1>Paciente X - Suspensión Tratamiento</h1>

            <div className="tabla-suspension">
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
                        <td>{tratamientoActivo.cantidad}</td>
                        <td>{tratamientoActivo.medicamento}</td>
                        <td>{tratamientoActivo.caracteristica}</td>
                        <td>{tratamientoActivo.frecuencia}</td>
                        <td>{tratamientoActivo.duracion}</td>
                    </tr>
                    </tbody>
                </table>

                <div className="porcentaje">
                    <p>Porcentaje cumplimiento tratamiento</p>
                    <span>{tratamientoActivo.cumplimiento}</span>
                </div>

                <div className="recomendaciones">
                    <label htmlFor="motivo">Motivo de cancelación de tratamiento:</label>
                    <textarea
                        id="motivo"
                        placeholder="Escribe aquí el motivo..."
                        defaultValue="No cumple con el tratamiento"
                    />
                </div>
            </div>
            <div className="actions">
                <button className="confirmar" onClick={suspender}>Suspender tratamiento</button>
                <button className="cancelar" onClick={() => navigate(-1)}>Regresar</button>
            </div>

            {mostrarModal && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h2>Tratamiento suspendido</h2>
                        <button onClick={aceptar} className="modal-aceptar">Aceptar</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default SuspenderTratamiento;
