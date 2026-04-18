function PatientList({ patients, assignPatient, prioritizePatient, cancelPatient, numConsultorios = 2 }) {
  const handlePrioritize = (patient) => {
    if (window.confirm(`¿Está seguro de que desea priorizar a ${patient.name}? Esto lo moverá al inicio de la lista.`)) {
      prioritizePatient(patient.id);
    }
  };

  if (patients.length === 0) {
    return (
      <div className="empty-state">
        <p>No hay pacientes en espera en este momento.</p>
      </div>
    );
  }

  return (
    <div className="patient-list">
      {patients.map((p, index) => (
        <div className="patient-item" key={p.id}>
          <div className="patient-info">
            <span className="patient-name">
              {index === 0 && patients.length > 1 && <span title="Prioritario" style={{ marginRight: '0.5rem' }}>🚩</span>}
              {p.name}
            </span>
            <span className="patient-status"> En espera</span>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {/* Botón de Priorizar (solo si no es el primero) */}
            {index !== 0 && (
              <button 
                className="btn-outline" 
                onClick={() => handlePrioritize(p)}
                title="Priorizar (Urgente)"
                style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}
              >
                🚩
              </button>
            )}

            {Array.from({ length: numConsultorios }, (_, i) => (
              <button
                key={i}
                className="btn-outline"
                onClick={() => assignPatient(p, i)}
                title={`Asignar a Consultorio ${i + 1}`}
              >
                C{i + 1}
              </button>
            ))}
            <button 
              className="btn-outline" 
              onClick={() => cancelPatient(p.id)}
              title="Cancelar paciente"
              style={{ color: '#ef4444', borderColor: '#fee2e2' }}
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PatientList;