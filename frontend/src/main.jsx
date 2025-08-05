import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'

import './common/styles/normalize.css'
import "./common/styles/index.css"

import Midas from "./features/feature_Grupo1_EvaluacionMidas/pages/Midas.jsx"
import Resultados from "./features/feature_Grupo1_EvaluacionMidas/pages/Resultados.jsx"
import Dashboard from './pages/paciente/Dashboard.jsx'

import Login from './pages/Login.jsx'
import AnalisisPatrones from './features/feature_Grupo6_AnalisisPatrones/pages/AnalisisPatrones'
import MDashboard from './features/feature_Grupo5_AgendamientoCitas/pages/DashboardMedicoPage.jsx'

import BDoctor from '@/features/feature_Grupo2_BitacoraAsistidaCefalea/pages/Bitacora-Medico.jsx'
import BPaciente from '@/features/feature_Grupo2_BitacoraAsistidaCefalea/pages/Bitacora-Paciente.jsx'
import RegistroCefalea from '@/features/feature_Grupo2_BitacoraAsistidaCefalea/pages/Registro-cefalea.jsx'
import Registro from './features/feature_Grupo3_Recordatorios/pages/Registro.jsx'

import MidasMedico from './features/feature_Grupo1_EvaluacionMidas/pages/MidasMedico.jsx'
import MidasEstadisticas from './features/feature_Grupo1_EvaluacionMidas/pages/MidasEstadisticas.jsx'

import PrimerConsulta from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/PrimerConsulta.jsx";
import Seguimiento from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/Seguimiento.jsx";
import CrearTratamiento from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/CrearTratamiento.jsx";
import Tratamientos from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/Tratamientos.jsx";
import SuspenderTratamiento
    from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/SuspenderTratamiento.jsx";
import EditarTratamiento from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/EditarTratamiento.jsx";
import HistorialTratamientos
  from "./features/feature_Grupo7_GeneracionSeguimientoTratamiento/pages/HistorialTratamientos.jsx";


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/analisis-patrones" element={<AnalisisPatrones />} />
        <Route path="/bitacora-medico/:pacienteId" element={<BDoctor />} />
        <Route path="/midas/historial" element={<MidasMedico />} />
        <Route path="/bitacora-paciente" element={<BPaciente />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/registro-cefalea" element={<RegistroCefalea />} />
        <Route path="/dashboard-paciente" element={<Dashboard />} />
        <Route path="/dashboard-medico" element={<MDashboard />} />
        <Route path="/midas" element={<Midas />} />
        <Route path="/midas/resultados" element={<Resultados />} />
         <Route path='/midas/estadisticas' element={<MidasEstadisticas/>}/>
          <Route path="/primerConsulta" element={<PrimerConsulta />}/>
          <Route path="/primerConsulta/crearTratamiento" element={<CrearTratamiento />}/>
          <Route path="/seguimiento" element={<Seguimiento />}/>
          <Route path= "/seguimiento/crearTratamiento" element ={<CrearTratamiento />}/>
          <Route path="/seguimiento/tratamientos" element={<Tratamientos />}/>
          <Route path="/seguimiento/tratamientos/crearTratamiento" element={<CrearTratamiento />}/>
          <Route path="/seguimiento/tratamientos/crearTratamiento/suspenderTratamiento" element={<SuspenderTratamiento />}/>
          <Route path="/seguimiento/tratamientos/crearTratamiento/editarTratamiento" element={<EditarTratamiento />}/>
          <Route path="/historialTratamientos" element={<HistorialTratamientos />}/>
      </Routes>
    </Router>
  </StrictMode>,
)
