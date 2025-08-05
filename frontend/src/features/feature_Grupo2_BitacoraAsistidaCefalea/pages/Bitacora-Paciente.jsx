import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '@/common/components/Header.jsx';
import Tabla from '@/common/components/Tabla.jsx';
import { parseApiResponse, getErrorMessage, getApiUrl, getAuthHeaders } from '../utils/apiUtils.js';
import { transformEpisodio, COLUMNAS_EPISODIOS } from '../utils/episodioUtils.js';
import { EPISODIOS_ENDPOINT } from '../utils/constants.js';
import '@/features/feature_Grupo2_BitacoraAsistidaCefalea/styles/bitacora.module.css';

export default function BitacoraDigital() {
    const navigate = useNavigate();
    const [episodios, setEpisodios] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchEpisodios = async () => {
            try {
                setLoading(true);
                setError(null);

                const url = getApiUrl(EPISODIOS_ENDPOINT);
                console.log('Intentando conectar a:', url);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: getAuthHeaders(null, 'paciente')
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();
                console.log('Datos recibidos de la API:', data);

                const episodiosArray = parseApiResponse(data);
                const episodiosTransformados = episodiosArray.map(transformEpisodio);

                setEpisodios(episodiosTransformados);
            } catch (err) {
                console.error('Error al cargar episodios:', err);
                setError(getErrorMessage(err));
            } finally {
                setLoading(false);
            }
        };

        fetchEpisodios();
    }, []);

    const handleNuevoEpisodio = () => {
        navigate('/registro');
    };

    const handleVolver = () => {
        navigate('/dashboard-paciente');
    };

    return (
        <div>
            <Header
                title="Bitácora"
                onBack={handleVolver}
                primaryButtonText="Nuevo episodio"
                onPrimaryClick={handleNuevoEpisodio}
            />
            {loading && (
                <div style={{ padding: '20px', textAlign: 'center' }}>
                    Cargando episodios...
                </div>
            )}
            {error && (
                <div style={{ padding: '20px', color: 'red', textAlign: 'center' }}>
                    {error}
                </div>
            )}
            {!loading && !error && (
                <Tabla
                    data={episodios}
                    columns={COLUMNAS_EPISODIOS}
                    keyField="id"
                    emptyMessage="No hay episodios de cefalea registrados"
                />
            )}
        </div>
    );
}
