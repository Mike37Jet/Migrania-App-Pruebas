import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Header from '@/common/components/Header.jsx';
import Tabla from '@/common/components/Tabla.jsx';
import ModalFiltro from '../components/ModalFiltro.jsx';
import { parseApiResponse, getErrorMessageMedico, fetchPacienteInfo } from '../utils/apiUtils.js';
import { transformEpisodioMedico, COLUMNAS_EPISODIOS_MEDICO } from '../utils/episodioUtils.js';
import { BASE_URL, EPISODIOS_ENDPOINT, TEMP_TOKEN_MEDICO } from '../utils/constants.js';
import '@/features/feature_Grupo2_BitacoraAsistidaCefalea/styles/bitacora.module.css';

export default function BitacoraDigitalMedico() {
    const { pacienteId } = useParams(); // Obtener el ID del paciente desde la URL
    const [episodios, setEpisodios] = useState([]);
    const [episodiosOriginales, setEpisodiosOriginales] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showModalFiltro, setShowModalFiltro] = useState(false);
    const [nombrePaciente, setNombrePaciente] = useState("");

    useEffect(() => {
        const fetchEpisodios = async () => {
            if (!pacienteId) {
                setError('ID de paciente no proporcionado');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);

                // Obtener información del paciente
                const nombrePaciente = await fetchPacienteInfo(pacienteId, BASE_URL, TEMP_TOKEN_MEDICO);
                setNombrePaciente(nombrePaciente);
                console.log(nombrePaciente);


                // Obtener episodios del paciente
                const url = `${BASE_URL}${EPISODIOS_ENDPOINT}?paciente_id=${pacienteId}`;
                console.log('Intentando conectar a:', url);
                console.log('Base URL configurada:', BASE_URL);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': TEMP_TOKEN_MEDICO ? `Bearer ${TEMP_TOKEN_MEDICO}` : '',
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();
                console.log('Datos recibidos de la API:', data);

                const episodiosArray = parseApiResponse(data);
                const episodiosTransformados = episodiosArray.map(transformEpisodioMedico);

                setEpisodios(episodiosTransformados);
                setEpisodiosOriginales(episodiosTransformados);
            } catch (err) {
                console.error('Error al cargar episodios:', err);
                setError(getErrorMessageMedico(err));
            } finally {
                setLoading(false);
            }
        };

        fetchEpisodios();
    }, [pacienteId]);

    const handleNuevoEpisodio = () => {
        setShowModalFiltro(true);
    };

    const handleVolver = () => {
        console.log('Volver clickeado');
    };

    const handleConfirmarFiltro = (tipoFiltro) => {
        setFiltroActivo(tipoFiltro);

        if (tipoFiltro === "") {
            // Mostrar todos los episodios
            setEpisodios(episodiosOriginales);
        } else {
            // Filtrar por tipo de cefalea
            const episodiosFiltrados = episodiosOriginales.filter(episodio =>
                episodio.categoria_diagnostica === tipoFiltro
            );
            setEpisodios(episodiosFiltrados);
        }

        setShowModalFiltro(false);
    };

    const handleCancelarFiltro = () => {
        setShowModalFiltro(false);
    };

    return (
        <div>
            <Header
                title="Bitácora"
                onBack={handleVolver}
                primaryButtonText="Filtrar bitácora"
                onPrimaryClick={handleNuevoEpisodio}
                patientName={nombrePaciente}
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
                    columns={COLUMNAS_EPISODIOS_MEDICO}
                    keyField="id"
                    emptyMessage="No hay episodios de cefalea registrados"
                />
            )}
            {showModalFiltro && (
                <ModalFiltro
                    message="Seleccionar filtro para la bitácora"
                    onConfirm={handleConfirmarFiltro}
                    onCancel={handleCancelarFiltro}
                />
            )}
        </div>
    );
}
