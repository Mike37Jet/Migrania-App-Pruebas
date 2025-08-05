import "../styles/modal.css";

function Modal({ message, onConfirm, onCancel }) {
    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h3>{message}</h3>
                <div className="modal-buttons">
                    <button className="button-confirm" onClick={onConfirm}>
                        Sí
                    </button>
                    <button className="button-cancel" onClick={onCancel}>
                        No
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Modal;
