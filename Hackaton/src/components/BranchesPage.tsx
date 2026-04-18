import React from 'react';
import { BRANCHES } from '../data';

export const BranchesPage: React.FC = () => {
  return (
    <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 24px' }} className="animate-in">
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '36px', marginBottom: '8px' }}>Nuestras Sucursales</h1>
        <p className="text-muted" style={{ fontSize: '16px' }}>Encuentra tu clínica más cercana y conoce nuestros servicios.</p>
      </div>

      <div className="stats">
        <div className="stat"><div className="stat-n">{BRANCHES.length}</div><div className="stat-l">Ubicaciones</div></div>
        <div className="stat"><div className="stat-n">48</div><div className="stat-l">Especialistas</div></div>
        <div className="stat"><div className="stat-n">9</div><div className="stat-l">Servicios</div></div>
        <div className="stat"><div className="stat-n">24/7</div><div className="stat-l">Urgencias</div></div>
      </div>

      <div className="g3">
        {BRANCHES.map((b) => (
          <div key={b.id} className="branch-card">
            <div className="branch-top">{b.emoji}</div>
            <div className="branch-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <h3 style={{ margin: 0 }}>{b.name}</h3>
                <span className="badge badge-ok"><div className="badge-dot" />Activa</span>
              </div>
              <div className="branch-meta">
                <div style={{ display: 'flex', gap: '8px' }}><span>📍</span> <span>{b.addr}</span></div>
                <div style={{ display: 'flex', gap: '8px' }}><span>📞</span> <span>{b.phone}</span></div>
                <div style={{ display: 'flex', gap: '8px' }}><span>👨‍⚕️</span> <span>{b.docs} médicos disponibles</span></div>
              </div>
              <div style={{ 
                marginTop: '20px', 
                paddingTop: '16px', 
                borderTop: '1px solid var(--border)',
                fontSize: '12px', 
                color: 'var(--text-muted)',
                lineHeight: '1.6'
              }}>
                <strong style={{ color: 'var(--text)', display: 'block', marginBottom: '4px', fontSize: '11px', textTransform: 'uppercase' }}>Servicios destacados</strong>
                {b.svcs}
              </div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
};
