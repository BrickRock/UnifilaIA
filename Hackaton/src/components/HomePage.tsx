import React from 'react';

interface HomePageProps {
  user: any;
  setPage: (page: string) => void;
  activeAppt: any | null;
  onLeaveQueue: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({ user, setPage, activeAppt, onLeaveQueue }) => {
  return (
    <main style={{ maxWidth: '800px', margin: '0 auto', padding: '80px 24px' }} className="animate-in">
      
      {activeAppt && (
        <div className="card" style={{ 
          borderColor: 'var(--green)', 
          background: 'var(--green-lt)',
          padding: '24px', 
          marginBottom: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '24px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ 
              width: '48px', height: '48px', borderRadius: '12px', 
              background: 'var(--bg-card)', display: 'flex', 
              alignItems: 'center', justifyContent: 'center', fontSize: '20px'
            }}>
              ✨
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700' }}>Fila Virtual Activa</h3>
              <p style={{ margin: '2px 0 0', color: 'var(--text-muted)', fontSize: '14px' }}>
                Tu turno estimado: <strong style={{ color: 'var(--text)' }}>{activeAppt.range}</strong>
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn btn-ghost" style={{ background: 'var(--bg-card)' }} onClick={() => setPage('queue')}>
              Detalles
            </button>
            <button className="btn btn-danger-soft" onClick={onLeaveQueue}>
              Salir
            </button>
          </div>
        </div>
      )}

      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <h1 style={{ fontSize: '56px', marginBottom: '20px', letterSpacing: '-0.05em' }}>
          Hola, {user.name.split(' ')[0]}
        </h1>
        <p className="text-muted" style={{ fontSize: '20px', maxWidth: '540px', margin: '0 auto 56px', lineHeight: '1.6' }}>
          Tu salud es nuestra prioridad. Gestiona tu lugar en nuestra Unifila y recibe atención médica sin esperas innecesarias.
        </p>

        {!activeAppt && (
          <button 
            className="btn btn-primary" 
            style={{ padding: '18px 40px', fontSize: '17px', borderRadius: 'var(--r-lg)' }}
            onClick={() => setPage('queue')}
          >
            Ingresar a la Unifila
          </button>
        )}
      </div>
    </main>
  );
};
