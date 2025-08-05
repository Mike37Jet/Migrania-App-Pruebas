import React from 'react';
import styles from '../styles/AnalisisPatrones.module.css';

export default function TarjetaAnalisis({ titulo, descripcion, recomendacion, icono }) {
    return (
        <div className={styles.tarjetaAnalisis}>
            <div className={styles.tarjetaAnalisis__cabecera}>
                {}
                {icono && <span className={styles.tarjetaAnalisis__icono}>{icono}</span>}
                <div className={styles.tarjetaAnalisis__texto}>
                    <h3 className={styles.tarjetaAnalisis__titulo}>{titulo}</h3>
                    <p className={styles.tarjetaAnalisis__descripcion}>{descripcion}</p>
                </div>
            </div>
            <div className={styles.tarjetaAnalisis__recomendacion}>
                <p><strong>Recomendación:</strong></p>
                <p>{recomendacion}</p>
            </div>
        </div>
    );
}