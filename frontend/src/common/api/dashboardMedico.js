export async function getDashboardMedico() {
  // Cuando conectes con el backend, cambia la URL:
  // const response = await fetch("/api/dashboard-medico/");
  // return await response.json();

  // Mock temporal para desarrollo visual:
  return {
    estadisticas: {
      pacientesTotales: 127,
      citasAgendadas: 8,
      casosUrgentes: 2,
    },
    alertasRecientes: [
      {
        id: 1,
        paciente: "Juan Guarnizo",
        episodio: "Episodio Severo",
        intensidad: "8/10",
        tiempo: "Hace 1 hora",
      },
      {
        id: 2,
        paciente: "Raúl Álvarez",
        episodio: "Episodio Severo",
        intensidad: "9/10",
        tiempo: "Hace 2 horas",
      },
    ],
    citasProximas: [
      {
        id: 1,
        dia: "01",
        mes: "JUL",
        doctor: "Dr. Juan Guarnizo",
        fecha: "01-07-2025",
        hora: "01:00 P.M.",
      },
    ],
  };
}
