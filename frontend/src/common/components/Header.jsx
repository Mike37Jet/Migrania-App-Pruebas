import React from 'react';
import { IoArrowBack, IoAdd, IoFilter } from 'react-icons/io5';

export default function Header({ title, onBack, primaryButtonText, onPrimaryClick, patientName }) {
    const displayTitle = patientName ? `${title} de ${patientName}` : title;
    
    const getButtonIcon = () => {
        if (primaryButtonText?.includes('Nuevo episodio')) {
            return <IoAdd />;
        }
        if (primaryButtonText?.includes('Filtrar bitácora')) {
            return <IoFilter />;
        }
        return null;
    };

    return (
        <header>
            <button className='btn-back' onClick={onBack}>
                <IoArrowBack />
                Volver
            </button>
            <h1>{displayTitle}</h1>
            {primaryButtonText && (
                <button className='btn-primary' onClick={onPrimaryClick}>
                    {getButtonIcon()}
                    {primaryButtonText}
                </button>
            )}
        </header>
    );
}
