import React, { useState } from "react";
import "@/common/styles/modal.css";
import "../styles/styles.css";

function ModalFiltro({ message, onConfirm, onCancel }) {
    const [selectedFilter, setSelectedFilter] = useState("");

    const tiposCefalea = [
        { value: "", label: "Todos los tipos" },
        { value: "Migraña sin aura", label: "Migraña sin aura" },
        { value: "Migraña con aura", label: "Migraña con aura" },
        { value: "Cefalea de tipo tensional", label: "Cefalea de tipo tensional" }
    ];

    const handleConfirm = () => {
        onConfirm(selectedFilter);
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h3>{message}</h3>

                <div className="filter-section">
                    <label htmlFor="tipo-cefalea-filter" className="filter-label">
                        Filtrar por tipo de cefalea:
                    </label>
                    <select
                        id="tipo-cefalea-filter"
                        className="filter-select"
                        value={selectedFilter}
                        onChange={(e) => setSelectedFilter(e.target.value)}
                    >
                        {tiposCefalea.map((tipo) => (
                            <option key={tipo.value} value={tipo.value}>
                                {tipo.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="modal-buttons">
                    <button className="button-confirm" onClick={handleConfirm}>
                        Aplicar Filtro
                    </button>
                    <button className="button-cancel" onClick={onCancel}>
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ModalFiltro;
