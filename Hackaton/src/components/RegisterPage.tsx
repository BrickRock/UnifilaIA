import React, { useState } from 'react';
import { demoAppts } from '../utils';
import { PATH } from '../api';

interface RegisterPageProps {
  setPage: (page: string) => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ setPage }) => {
  const [f, setF] = useState({ name: '', ap1: '', curp: '', nss: '', birthDate: '', isChronic: false });
  const [err, setErr] = useState('');
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!f.name || !f.ap1 || !f.curp || !f.nss || !f.birthDate) return setErr('Por favor completa todos los campos obligatorios.');
    const curp = f.curp.trim().toUpperCase();
    if (curp.length !== 18) return setErr('La CURP debe tener exactamente 18 caracteres.');
    if (f.nss.length !== 11) return setErr('El NSS debe tener 11 dígitos.');
    
    setLoading(true);
    setErr('');

    // Extracting gender from CURP and mapping to M/F as expected by IMSS schemas
    // CURP: H -> M (Masculino), M -> F (Femenino)
    const curpGender = curp.substring(10, 11);
    const mappedGender = curpGender === 'H' ? 'M' : 'F';

    const payload = {
      curp: curp,
      nss: f.nss,
      nombre_completo: `${f.name} ${f.ap1}`.trim(),
      fecha_nacimiento: f.birthDate,
      sexo: mappedGender,
      es_cronico: f.isChronic,
      es_cronico_general: f.isChronic
    };

    try {
      const response = await fetch(`${PATH}/pacientes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al registrar paciente');
      }

      setOk(true);
      setTimeout(() => setPage('login'), 1800);
    } catch (err: any) {
      setErr(err.message || 'Error de conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page animate-in">
      <div className="auth-card" style={{ maxWidth: '480px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Crear Cuenta</h1>
          <p className="text-muted" style={{ fontSize: '15px' }}>Regístrate para acceder a los servicios</p>
        </div>

        {err && (
          <div style={{ 
            background: 'rgba(220, 38, 38, 0.05)', 
            color: '#DC2626', 
            padding: '12px', 
            borderRadius: 'var(--r-sm)', 
            marginBottom: '20px', 
            fontSize: '13px', 
            textAlign: 'center',
            border: '1px solid rgba(220, 38, 38, 0.1)'
          }}>
            {err}
          </div>
        )}
        
        {ok && (
          <div style={{ 
            background: 'var(--green-lt)', 
            color: 'var(--green)', 
            padding: '12px', 
            borderRadius: 'var(--r-sm)', 
            marginBottom: '20px', 
            fontSize: '14px', 
            textAlign: 'center',
            fontWeight: '600'
          }}>
            ✓ Cuenta creada exitosamente
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="fg"><label>Nombre</label><input placeholder="Ej. Juan" value={f.name} onChange={(e) => setF({...f, name: e.target.value})} /></div>
          <div className="fg"><label>Apellido</label><input placeholder="Ej. Pérez" value={f.ap1} onChange={(e) => setF({...f, ap1: e.target.value})} /></div>
        </div>

        <div className="fg">
          <label>CURP</label>
          <input 
            className="curp-input" 
            maxLength={18} 
            placeholder="Ingresa tu CURP" 
            style={{ fontFamily: 'monospace', letterSpacing: '0.05em' }}
            value={f.curp} 
            onChange={(e) => setF({...f, curp: e.target.value.toUpperCase()})} 
          />
        </div>
        
        <div className="fg">
          <label>NSS (Número de Seguridad Social)</label>
          <input 
            maxLength={11} 
            placeholder="11 dígitos" 
            value={f.nss} 
            onChange={(e) => setF({...f, nss: e.target.value.replace(/\D/g, '')})} 
          />
        </div>

        <div className="fg">
          <label>Fecha de Nacimiento</label>
          <input 
            type="date"
            value={f.birthDate} 
            onChange={(e) => setF({...f, birthDate: e.target.value})} 
          />
        </div>

        <div className="fg" style={{ marginTop: '8px' }}>
          <div 
            onClick={() => setF({...f, isChronic: !f.isChronic})}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '16px', 
              background: f.isChronic ? 'var(--green-lt)' : 'transparent',
              border: `1px solid ${f.isChronic ? 'var(--green)' : 'var(--border)'}`,
              borderRadius: 'var(--r-sm)',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <div style={{
              width: '20px',
              height: '20px',
              borderRadius: '6px',
              border: `2px solid ${f.isChronic ? 'var(--green)' : 'var(--text-muted)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: f.isChronic ? 'var(--green)' : 'transparent',
              transition: 'all 0.2s'
            }}>
              {f.isChronic && (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              )}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '14px', fontWeight: '600', color: f.isChronic ? 'var(--green)' : 'var(--text)' }}>
                Paciente Crónico
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Tengo diagnosticada una enfermedad crónica
              </div>
            </div>
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%', marginTop: '24px', padding: '14px' }} disabled={loading} onClick={submit}>
          {loading ? 'Registrando...' : 'Completar Registro'}
        </button>

        <div style={{ marginTop: '32px', textAlign: 'center', fontSize: '14px' }}>
          <span className="text-muted">¿Ya tienes cuenta?</span>{' '}
          <button 
            style={{ 
              background: 'none', 
              border: 'none', 
              color: 'var(--text)', 
              fontWeight: '600', 
              cursor: 'pointer', 
              textDecoration: 'underline',
              textUnderlineOffset: '4px'
            }} 
            onClick={() => setPage('login')}
          >
            Inicia sesión
          </button>
        </div>
      </div>
    </div>
  );
};
