import React from 'react';
import styles from '../styles/AnalisisPatrones.module.css';

export default function TarjetaResumen({ titulo, valor, subtitulo, icono, color, iconColor }) {
    
    const backgroundColorVar = color === 'secondary-light' 
        ? `var(--${color})` 
        : `var(--color-${color})`;

    const cardStyle = {
        backgroundColor: backgroundColorVar
    };

    const iconStyle = {
        color: iconColor
    };

    return (
        <div className={styles.tarjetaResumen} style={cardStyle}>
            <h3 className={styles.tarjetaResumen__titulo}>{titulo}</h3>
            <div className={styles.tarjetaResumen__contenido}>
                
                <span className={styles.tarjetaResumen__icono} style={iconStyle}>{icono}</span>
                <span className={styles.tarjetaResumen__valor}>{valor}</span>
            </div>
            <p className={styles.tarjetaResumen__subtitulo}>{subtitulo}</p>
        </div>
    );
}