import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/editarTratamiento.css";

const recomendacionesHombre = [
    "Mantener una rutina regular de sueño",
    "Realizar ejercicio de forma moderada",
    "Controlar los niveles de estrés",
    "Mantener una hidratación adecuada",
    "Buscar un ambiente oscuro y silencioso para descansar durante el episodio",
    "Realizar una compresión fría o tibia sobre la zona afectada",
    "Evitar cualquier tipo de esfuerzo físico mientras dure el episodio",
    "Ingerir líquidos en pequeñas cantidades y evitar alimentos pesados"
];

const recomendacionesMujer = [
    ...recomendacionesHombre,
    "Utilizar analgésicos adecuados durante el periodo menstrual",
    "Consultar con un ginecólogo sobre anticonceptivos hormonales"
];

function EditarTratamiento({ genero = "hombre" }) {
    const navigate = useNavigate();
    const [mostrarModal, setMostrarModal] = useState(false);
    const [tratamientos, setTratamientos] = useState([
        { cantidad: 1, medicamento: "Analgésicos", caracteristica: "500mg", frecuencia: "C/8h", duracion: "3 días" }
    ]);
    const [recomendacionesSeleccionadas, setRecomendacionesSeleccionadas] = useState([
        "Mantener una rutina regular de sueño"
    ]);

    const recomendaciones = genero === "mujer" ? recomendacionesMujer : recomendacionesHombre;

    const handleAddFila = () => {
        setTratamientos([
            ...tratamientos,
            { cantidad: 1, medicamento: "", caracteristica: "", frecuencia: "", duracion: "" }
        ]);
    };

    const handleRemoveFila = (index) => {
        const nuevos = tratamientos.filter((_, i) => i !== index);
        setTratamientos(nuevos);
    };

    const handleInputChange = (index, field, value) => {
        const nuevos = [...tratamientos];
        nuevos[index][field] = value;
        setTratamientos(nuevos);
    };

    const handleToggleRecomendacion = (texto) => {
        setRecomendacionesSeleccionadas((prev) =>
            prev.includes(texto)
                ? prev.filter((r) => r !== texto)
                : [...prev, texto]
        );
    };

    const handleEnviar = () => {
        setMostrarModal(true);
    };

    const handleCerrarModal = () => {
        setMostrarModal(false);
        navigate("/home");
    };

    return (
        <div className="editar-tratamiento-container">
            <header>
                <div className="user-info">
                    <span className="user-icon">👤</span>
                    <span className="user-name">Dr. X</span>
                </div>
            </header>

            <h1>Paciente X – Editar Tratamiento</h1>

            <div className="editar-tratamiento-table-container">
                <table className="editar-tratamiento-table">
                    <thead>
                    <tr>
                        <th>Cantidad</th>
                        <th>Medicamento</th>
                        <th>Característica</th>
                        <th>Frecuencia</th>
                        <th>Duración Tratamiento</th>
                        <th>Acciones</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tratamientos.map((fila, index) => (
                        <tr key={index}>
                            <td>
                                <input
                                    type="number"
                                    min="1"
                                    value={fila.cantidad}
                                    onChange={(e) =>
                                        handleInputChange(index, "cantidad", parseInt(e.target.value))
                                    }
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={fila.medicamento}
                                    onChange={(e) =>
                                        handleInputChange(index, "medicamento", e.target.value)
                                    }
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={fila.caracteristica}
                                    onChange={(e) =>
                                        handleInputChange(index, "caracteristica", e.target.value)
                                    }
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={fila.frecuencia}
                                    onChange={(e) =>
                                        handleInputChange(index, "frecuencia", e.target.value)
                                    }
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={fila.duracion}
                                    onChange={(e) =>
                                        handleInputChange(index, "duracion", e.target.value)
                                    }
                                />
                            </td>
                            <td className="editar-tratamiento-botones">
                                <button className="editar-tratamiento-add" onClick={handleAddFila}>+</button>
                                {tratamientos.length > 1 && (
                                    <button
                                        className="editar-tratamiento-remove"
                                        onClick={() => handleRemoveFila(index)}
                                    >−</button>
                                )}
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
                <div className="editar-tratamiento-recomendaciones">
                    <h3>Recomendaciones</h3>
                    <div className="editar-tratamiento-lista">
                        {recomendaciones.map((texto, i) => (
                            <label key={i}>
                                <input
                                    type="checkbox"
                                    checked={recomendacionesSeleccionadas.includes(texto)}
                                    onChange={() => handleToggleRecomendacion(texto)}
                                />
                                {texto}
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            <div className="editar-tratamiento-actions">
                <button className="editar-tratamiento-enviar" onClick={handleEnviar}>
                    Enviar tratamiento
                </button>
                <button className="editar-tratamiento-cancelar" onClick={() => navigate(-1)}>
                    Regresar
                </button>
            </div>

            {mostrarModal && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h2>Tratamiento modificado y enviado</h2>
                        <button onClick={handleCerrarModal}>Aceptar</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default EditarTratamiento;
