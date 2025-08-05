import React from 'react';

export default function Tabla({
    data = [],
    columns = [],
    keyField = 'id',
    className = 'table-container',
    emptyMessage = 'No hay datos disponibles'
}) {
    const generarColumnasAutomaticas = (primerElemento) => {
        return Object.keys(primerElemento).map(nombreCampo => ({
            key: nombreCampo,
            header: formatearNombreCampo(nombreCampo),
            render: (valor) => valor
        }));
    };

    const formatearNombreCampo = (nombreCampo) => {
        return nombreCampo
            .charAt(0).toUpperCase() +
            nombreCampo.slice(1)
                .replace(/_/g, ' ');
    };

    const obtenerColumnas = () => {
        if (columns.length > 0) {
            return columns;
        }

        if (data.length > 0) {
            return generarColumnasAutomaticas(data[0]);
        }

        return [];
    };

    const tableColumns = obtenerColumnas();

    const renderizarContenidoCelda = (fila, columna) => {
        const valor = fila[columna.key];
        if (columna.render && typeof columna.render === 'function') {
            return columna.render(valor, fila);
        }
        return valor !== null && valor !== undefined ? valor : '-';
    };

    const TablaVacia = () => (
        <div className="empty-table">
            <p>{emptyMessage}</p>
        </div>
    );

    const EncabezadosTabla = () => (
        <thead>
            <tr>
                {tableColumns.map((columna) => (
                    <th key={columna.key}>
                        {columna.header}
                    </th>
                ))}
            </tr>
        </thead>
    );

    const CuerpoTabla = () => (
        <tbody>
            {data.map((fila, indice) => (
                <tr key={fila[keyField] || indice}>
                    {tableColumns.map((columna) => (
                        <td key={columna.key}>
                            {renderizarContenidoCelda(fila, columna)}
                        </td>
                    ))}
                </tr>
            ))}
        </tbody>
    );

    return (
        <div className={className}>
            {data.length === 0 ? (
                <TablaVacia />
            ) : (
                <table>
                    <EncabezadosTabla />
                    <CuerpoTabla />
                </table>
            )}
        </div>
    );
}
