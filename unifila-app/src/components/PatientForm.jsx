import { useState } from "react";

function PatientForm({ addPatient }) {
  const [name, setName] = useState("");
  const [vitals, setVitals] = useState({
    preventiva: 0,
    mas_de_un_sintoma: 0,
    adulto: 0,
    comorbilidad: 0,
    tiene_laboratorio: 0,
    es_seguimiento: 0
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleToggle = (field) => {
    setVitals(prev => ({
      ...prev,
      [field]: prev[field] === 1 ? 0 : 1
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || isSubmitting) return;

    setIsSubmitting(true);
    // Enviamos el nombre para la UI y el objeto vitals que cumple con TurnoCreate
    await addPatient(name.trim(), vitals);
    
    setName("");
    setVitals({
      preventiva: 0,
      mas_de_un_sintoma: 0,
      adulto: 0,
      comorbilidad: 0,
      tiene_laboratorio: 0,
      es_seguimiento: 0
    });
    setIsSubmitting(false);
  };

  const fields = [
    { id: "preventiva", label: "Acción Preventiva" },
    { id: "mas_de_un_sintoma", label: "Más de un Síntoma" },
    { id: "adulto", label: "Adulto Mayor (65+)" },
    { id: "comorbilidad", label: "Comorbilidad" },
    { id: "tiene_laboratorio", label: "Trae Laboratorio" },
    { id: "es_seguimiento", label: "Es Seguimiento" }
  ];

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-field" style={{ marginBottom: '2rem' }}>
        <label>NOMBRE DEL PACIENTE</label>
        <input
          type="text"
          placeholder="Ej. Juan Pérez"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={isSubmitting}
          required
        />
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '1rem', 
        marginBottom: '2rem' 
      }}>
        {fields.map((field) => (
          <div 
            key={field.id}
            onClick={() => !isSubmitting && handleToggle(field.id)}
            style={{
              padding: '1rem',
              borderRadius: '8px',
              border: '1px solid',
              borderColor: vitals[field.id] ? 'var(--primary)' : '#ddd',
              backgroundColor: vitals[field.id] ? 'rgba(37, 99, 235, 0.1)' : 'transparent',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              transition: 'all 0.2s'
            }}
          >
            <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>{field.label}</span>
            <div style={{
              width: '20px',
              height: '20px',
              borderRadius: '4px',
              border: '2px solid var(--primary)',
              backgroundColor: vitals[field.id] ? 'var(--primary)' : 'transparent',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
              fontSize: '12px'
            }}>
              {vitals[field.id] ? '✓' : ''}
            </div>
          </div>
        ))}
      </div>

      <button 
        className="btn-primary" 
        type="submit" 
        style={{ width: '100%', padding: '1.5rem' }}
        disabled={isSubmitting}
      >
        {isSubmitting ? "REGISTRANDO..." : "REGISTRAR TURNO"}
      </button>
    </form>
  );
}

export default PatientForm;
