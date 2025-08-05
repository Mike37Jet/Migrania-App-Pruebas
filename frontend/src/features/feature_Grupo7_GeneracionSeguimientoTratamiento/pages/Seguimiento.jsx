import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/seguimiento.css";
import ConfirmacionCancelar from "@/features/feature_Grupo7_GeneracionSeguimientoTratamiento/components/ConfirmacionCancelar.jsx";

function Seguimiento() {
    const navigate = useNavigate();
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [doctorName, setDoctorName] = useState("");
    const [patientName, setPatientName] = useState("Paciente X");
    const [episodeData, setEpisodeData] = useState([]);

    useEffect(() => {
        setDoctorName("Dr. X");
        setPatientName("Juan Pérez");
        // Simulando los episodios de un paciente
        setEpisodeData([
            { num: 1, tipo: "Migraña", fecha: "10/08/2025", tratamiento: "Activo" },
            { num: 2, tipo: "Cefalea tensional", fecha: "12/08/2025", tratamiento: "S/T" },
        ]);
    }, []);

    const handleCancel = () => {
        setIsModalVisible(true);
    };

    const handleCloseModal = () => {
        setIsModalVisible(false);
    };

    const handleNavigateHistorial = () => {
        navigate("/historial");
    };

    const handleNavigateCrearTratamiento = () => {
        navigate("/seguimiento/crearTratamiento");
    };

    const handleNavigateTratamientos = () => {
        navigate("/seguimiento/tratamientos");
    }

    return (
        <div className="container">
            <header>
                <div className="user-info">
                    <span className="user-icon">👤</span>
                    <span className="user-name">{doctorName}</span>
                </div>
            </header>

            <div className="patient-info">
                <h1>{patientName} - Seguimiento</h1>
                <button className="history-button" onClick={handleNavigateHistorial}>
                    Historial
                </button>

                <button className="tratamiento-button" onClick={handleNavigateTratamientos}>
                    Tratamiento
                </button>
            </div>

            <div className="table-container">
                <table>
                    <thead>
                    <tr>
                        <th>Num. Episodio</th>
                        <th>Tipo Episodio</th>
                        <th>Fecha</th>
                        <th>Tratamiento</th>
                    </tr>
                    </thead>
                    <tbody>
                    {episodeData.map((episode) => (
                        <tr key={episode.num}>
                            <td>{episode.num}</td>
                            <td>{episode.tipo}</td>
                            <td>{episode.fecha}</td>
                            <td>{episode.tratamiento}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            <div className="actions">
                <button className="action-button create-treatment" onClick={handleNavigateCrearTratamiento}>
                    Crear tratamiento
                </button>
                <button className="action-button cancel" onClick={handleCancel}>
                    Cancelar
                </button>
            </div>

            {isModalVisible && <ConfirmacionCancelar onClose={handleCloseModal} />}
        </div>
    );
}

export default Seguimiento;