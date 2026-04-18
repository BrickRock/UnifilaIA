import React, { useState } from 'react';
import { makeJWT } from '../utils';
import { PATH } from '../api';

interface LoginPageProps {
  setUser: (user: any) => void;
  setPage: (page: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ setUser, setPage }) => {
  const [nss, setNss] = useState('');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    const val = nss.trim();
    if (val !== 'admin' && val.length !== 11) return setErr('Ingresa un NSS válido (11 dígitos).');
    setErr(''); setLoading(true);

    try {
      const response = await fetch(`${PATH}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: val, password: 'admin' }) 
      });

      if (!response.ok) throw new Error('Credenciales inválidas');

      // Intentar obtener datos del paciente usando el NSS como identificador
      // Nota: Si el backend requiere CURP para /pacientes/, necesitaremos que el login devuelva el perfil
      let userData = { nss: val, name: 'Paciente' };
      
      localStorage.setItem('mc_token', 'fake-token'); 
      setUser(userData);
      setPage('home');
    } catch (err) {
      setErr('Error al iniciar sesión. Verifica tu NSS.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page animate-in">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <img 
            src="/IMSS_Logosímbolo.png" 
            alt="IMSS Logo" 
            style={{ width: '80px', height: 'auto', marginBottom: '16px' }} 
          />
          <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Bienvenido</h1>
          <p className="text-muted" style={{ fontSize: '15px' }}>Ingresa tu NSS para continuar</p>
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

        <div className="fg">
          <label>Número de Seguridad Social (NSS)</label>
          <input
            className="nss-input"
            maxLength={11}
            placeholder="00000000000"
            style={{ 
              letterSpacing: '0.1em', 
              textAlign: 'center', 
              fontFamily: 'monospace',
              fontSize: '22px'
            }}
            value={nss}
            onChange={(ev) => setNss(ev.target.value.replace(/\D/g, ''))}
            onKeyDown={(ev) => ev.key === 'Enter' && submit()}
          />
        </div>

        <button className="btn btn-primary" style={{ width: '100%', padding: '14px' }} onClick={submit} disabled={loading}>
          {loading ? 'Verificando...' : 'Acceder'}
        </button>

        <div style={{ marginTop: '32px', textAlign: 'center', fontSize: '14px' }}>
          <span className="text-muted">¿Nuevo aquí?</span>{' '}
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
            onClick={() => setPage('register')}
          >
            Crea una cuenta
          </button>
        </div>
      </div>
    </div>
  );
};
