import { useState, useEffect } from "react";
import PatientForm from "../components/PatientForm";
import PatientList from "../components/PatientList";
import Consultorio from "../components/Consultorio";
import { api } from "../services/api";

function Home({ patients, addPatient, prioritizePatient, cancelPatient, removePatientFromList }) {
  const [consultoriosMeta, setConsultoriosMeta] = useState([]);
  const [consultorios, setConsultorios] = useState([]);

  useEffect(() => {
    api.getConsultorios()
      .then(data => {
        setConsultoriosMeta(data);
        setConsultorios(Array(data.length).fill(null));
      })
      .catch(err => console.error("Error cargando consultorios:", err));
  }, []);

  const assignPatient = (patient, index) => {
    const updated = [...consultorios];
    updated[index] = patient;
    setConsultorios(updated);
    removePatientFromList(patient.id);
  };

  const clearConsultorio = (index) => {
    const updated = [...consultorios];
    updated[index] = null;
    setConsultorios(updated);
  };
//C:\Users\matba\Downloads\ProyectoUNIFILA\unifila-app\src\components\Consultorio.jsx
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <main className="app-container">
        {/* Hero Corporativo - Regresado a Fase 6 */}
        <section className="hero-section">
          <div className="hero-content">
            <h1>Optimización Inteligente del Flujo de Pacientes</h1>
            <p>La plataforma líder en gestión de triage y eficiencia hospitalaria en tiempo real.</p>
          </div>
          <div className="queue-illustration">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="queue-person" style={{ animationDelay: `${i * 0.2}s` }}></div>
            ))}
          </div>
        </section>

        {/* Faja de Beneficios - Fase 6 */}
        <section className="features-row">
          <div className="feature-card">
            <span style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}>🛡️</span>
            <div style={{ fontWeight: '800', marginBottom: '0.5rem' }}>Seguridad Clínica</div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Gestión avanzada de signos vitales y triage.</p>
          </div>
          <div className="feature-card">
            <span style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}>📊</span>
            <div style={{ fontWeight: '800', marginBottom: '0.5rem' }}>Monitoreo Real</div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Control total de lista y consultorios.</p>
          </div>
          <div className="feature-card">
            <span style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}>⚡</span>
            <div style={{ fontWeight: '800', marginBottom: '0.5rem' }}>Alta Eficiencia</div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Priorización inteligente de urgencias.</p>
          </div>
        </section>

        {/* Dashboard - Grid Fase 6 */}
        <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '3rem' }}>
          <section className="dashboard-left">
            <div className="card">
              <h2><span>🟢</span> Registro de Admisión</h2>
              <PatientForm addPatient={addPatient} />
            </div>

            <div className="card">
              <h2><span>🕒</span> Central de Espera</h2>
              <PatientList
                patients={patients}
                assignPatient={assignPatient}
                prioritizePatient={prioritizePatient}
                cancelPatient={cancelPatient}
                numConsultorios={consultoriosMeta.length}
              />
            </div>
          </section>

          <section className="dashboard-right">
            <div className="card" style={{ height: 'calc(100% - 3rem)' }}>
              <Consultorio
                consultorios={consultorios}
                meta={consultoriosMeta}
                clearConsultorio={clearConsultorio}
              />
            </div>
          </section>
        </div>
      </main>

      {/* Footer Fase 6 */}
      <footer className="footer">
        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginBottom: '1.5rem' }}>
          <a href="#" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Soporte</a>
          <a href="#" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Privacidad</a>
        </div>
        <p className="footer-copy">© 2026 Unifila Health Inc. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}

export default Home;