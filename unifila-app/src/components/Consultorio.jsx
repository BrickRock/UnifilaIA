function Consultorio({ consultorios, clearConsultorio }) {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2 style={{ margin: 0 }}><span>🩺</span> Estado de Consultorios</h2>
      </div>

      <div className="rooms-container" style={{ flex: 1 }}>
        {consultorios.map((patient, index) => (
          <div key={index} className={`room-card ${patient ? 'occupied' : 'blink'}`}>
            <div className="room-name">Consultorio {index + 1}</div>
            
            <div className="occupant-name">
              {patient ? patient.name : "VACÍO"}
            </div>

            {patient ? (
              <button 
                className="btn-danger" 
                style={{ width: '100%' }}
                onClick={() => clearConsultorio(index)}
              >
                <span>✅</span> Finalizar
              </button>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Esperando paciente...
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div style={{ marginTop: '2rem', padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        <strong>Tip:</strong> Use el botón 🚩 en la lista de espera para mover pacientes urgentes al inicio de la fila.
      </div>
    </div>
  );
}

export default Consultorio;