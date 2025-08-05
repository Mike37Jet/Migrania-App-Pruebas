import React from "react";
import estilos from "../styles/DashboardMedico.module.css";
import comunes from "../styles/common.module.css";
import { useNavigate } from "react-router-dom";

const DashboardMedico = ({ estadisticas, alertasRecientes, citasProximas }) => {
  const navegar = useNavigate();

  const manejarVerAgenda = () => navegar("/agenda/semana");
  const manejarVolver = () => navegar(-1);

  return (
    <div className={estilos.dashboardContainer}>
      <header className={comunes.header}>
        <button
          className={comunes["btn-back"]}
          onClick={manejarVolver}
          aria-label="Volver"
        >
          ← Volver
        </button>
        <h1 className={comunes.title}>Citas Médicas</h1>
        <div />
      </header>

      <div className={estilos.statsGrid}>
        <div className={estilos.statCard}>
          <div className={estilos.statIcon}>👥</div>
          <div>
            <div className={estilos.statNumber}>
              {estadisticas.pacientesTotales}
            </div>
            <div className={estilos.statLabel}>Pacientes Totales</div>
          </div>
        </div>
        <div className={estilos.statCardLight}>
          <div className={estilos.statIcon}>🩺</div>
          <div>
            <div className={estilos.statNumber}>
              {estadisticas.citasAgendadas}
            </div>
            <div className={estilos.statLabel}>Citas Agendadas</div>
          </div>
        </div>
        <div className={estilos.statCardAlert}>
          <div className={estilos.statIcon}>🚨</div>
          <div>
            <div className={estilos.statNumber}>
              {estadisticas.casosUrgentes}
            </div>
            <div className={estilos.statLabelAlert}>Casos Urgentes</div>
          </div>
        </div>
      </div>

      <div className={estilos.sections}>
        <section className={estilos.alertSection}>
          <h2>Alertas Recientes</h2>
          <div>
            {alertasRecientes.map((a) => (
              <div key={a.id} className={estilos.alertCard}>
                <div className={estilos.alertAvatar}></div>
                <div>
                  <div className={estilos.alertPaciente}>
                    {a.paciente} - {a.episodio}
                  </div>
                  <div className={estilos.alertDetalles}>
                    <span>Intensidad {a.intensidad}</span>
                    <span className={estilos.alertTiempo}>🕘 {a.tiempo}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
        <section className={estilos.nextSection}>
          <h2>Citas Próximas</h2>
          <div>
            {citasProximas.map((c) => (
              <div key={c.id} className={estilos.nextCard}>
                <div className={estilos.nextFecha}>
                  <div className={estilos.nextDia}>{c.dia}</div>
                  <div className={estilos.nextMes}>{c.mes}</div>
                </div>
                <div>
                  <div className={estilos.nextDoctor}>👨‍⚕️ {c.doctor}</div>
                  <div className={estilos.nextDetalles}>📅 {c.fecha}</div>
                  <div className={estilos.nextHora}>🕘 {c.hora}</div>
                </div>
              </div>
            ))}
          </div>
          <button className={comunes["btn-primary"]} onClick={manejarVerAgenda}>
            Ver Agenda
          </button>
        </section>
      </div>
    </div>
  );
};

export default DashboardMedico;
