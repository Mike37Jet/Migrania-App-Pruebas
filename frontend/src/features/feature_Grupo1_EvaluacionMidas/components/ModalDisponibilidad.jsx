import styles from "../styles/ModalDisponibilidad.module.css";

export default function ModalDisponibilidad({ onClose }) {
    return (
        <div className={styles["modal__overlay"]}>
            <div className={styles["modal__contenedor"]}>
                <h2 className={styles["modal__titulo"]}>Bienvenido a la Autoevaluación MIDAS</h2>
                <p className={styles["modal__mensaje"]}>
                    Esta evaluación te tomará unos minutos. Por favor responde con honestidad.
                </p>
                <button className="btn-primary" onClick={onClose}>
                    Comenzar
                </button>
            </div>
        </div>
    );
}