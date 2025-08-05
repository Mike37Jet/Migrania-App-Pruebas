import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/tratamientos.css";

function Tratamientos() {
    const navigate = useNavigate();

    const tratamientos = [
        {
            id: 1,
            episodio: 2,
            fecha: "dd/mm/aa",
            estado: "Activo",
            cumplimiento: "50%",
        },
        {
            id: 2,
            episodio: 1,
            fecha: "dd/mm/aa",
            estado: "Finalizado",
            cumplimiento: "50%",
        },
    ];

    return (
        <div className="tratamientos">
            <header>
                <div className="user-info">
                    <span className="user-icon">👤</span>
                    <span className="user-name">Dr. X</span>
                </div>
            </header>

            <div className="patient-info">
                <h1>Paciente X - Tratamientos</h1>
                <button className="history-button">Historial</button>
            </div>

            <div className="table-container">
                <table>
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
                            <td className="acciones">
                                <button
                                    className="edit-button"
                                    onClick={() => navigate("/seguimiento/tratamientos/crearTratamiento/editarTratamiento")}
                                >
                                    Editar
                                </button>
                                <button
                                    className="delete-button"
                                    onClick={() => navigate("/seguimiento/tratamientos/crearTratamiento/suspenderTratamiento")}
                                >
                                    Suspender
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            <div className="actions">
                <button
                    className="create-treatment"
                    onClick={() => navigate("/seguimiento/tratamientos/crearTratamiento")}
                >
                    Nuevo tratamiento
                </button>
                <button className="cancel" onClick={() => navigate(-1)}>
                    Cancelar
                </button>
            </div>
        </div>
    );
}

export default Tratamientos;
