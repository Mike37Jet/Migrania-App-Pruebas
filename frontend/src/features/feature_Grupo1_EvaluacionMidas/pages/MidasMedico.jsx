import TablaExpandible from "../components/TablaExpandible";
const datosEjemplo = [
    {
        id: 1,
        fechaEvaluacion: "2025-08-01",
        respuestas: [2, 5, 3, 4, 1],
    },
    {
        id: 2,
        fechaEvaluacion: "2025-08-03",
        respuestas: [0, 0, 1, 2, 1],
    },
];


export default function MidasMedico() {

    return <div>
        <h1>Autoevaluaciones Pasadas</h1>
        <TablaExpandible data={datosEjemplo} />

    </div>
}