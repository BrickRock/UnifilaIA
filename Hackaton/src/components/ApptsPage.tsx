import React, { useState, useEffect } from 'react';
import { BookModal } from './BookModal';
import { ST } from '../data';

interface ApptsPageProps {
  user: any;
}

export const ApptsPage: React.FC<ApptsPageProps> = ({ user }) => {
  const [appts, setAppts] = useState<any[]>([]);
  const [modal, setModal] = useState(false);
  const [tab, setTab] = useState('all');

  const load = () => setAppts(JSON.parse(localStorage.getItem('mc_appts_' + user.curp) || '[]'));
  
  useEffect(() => {
    load();
  }, [user.curp]);

  const cancel = (id: number) => {
    const list = appts.map((a) => (a.id === id ? { ...a, status: 'cancelled', note: 'Cancelada por el paciente' } : a));
    localStorage.setItem('mc_appts_' + user.curp, JSON.stringify(list));
    setAppts(list);
  };

  const TABS: Record<string, string> = { all: 'Todas', pending: 'Pendientes', confirmed: 'Confirmadas', cancelled: 'Canceladas' };
  
  const filtered = tab === 'all' ? appts : appts.filter((a) =>
    tab === 'cancelled' ? (a.status === 'cancelled' || a.status === 'delayed') : a.status === tab
  );

  return (
    <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 24px' }} className="animate-in">
      {modal && <BookModal user={user} onClose={() => setModal(false)} onSave={load} />}
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', gap: '20px', flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '4px' }}>Mis Citas</h1>
          <p className="text-muted" style={{ fontSize: '15px' }}>Gestiona tus horarios y consultas médicas</p>
        </div>
        <button className="btn btn-primary" style={{ padding: '12px 24px' }} onClick={() => setModal(true)}>
          Agendar Nueva Cita
        </button>
      </div>

      <div className="tabs">
        {Object.entries(TABS).map(([k, v]) => (
          <button key={k} className={`tab ${tab === k ? ' on' : ''}`} onClick={() => setTab(k)}>
            {v}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div style={{ padding: '80px 24px', textAlign: 'center', background: 'var(--bg-card)', borderRadius: 'var(--r)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>📋</div>
          <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>Sin citas encontradas</h3>
          <p className="text-muted">No hay citas en esta categoría. Puedes agendar una nueva en el botón superior.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '16px' }}>
          {filtered.map((a) => {
            const st = (ST as any)[a.status] || ST.pending;
            return (
              <div key={a.id} className="ac">
                <div className={`ac-stripe ${st.stripe}`} />
                <div className="ac-info" style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0 }}>{a.spec}</h3>
                    <span className={`badge ${st.cls}`}><div className="badge-dot" />{st.label}</span>
                  </div>
                  <div className="ac-meta">
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>📅 {a.date}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>🕒 {a.time}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>🏥 {a.branch}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>🚪 Cons. {a.consultory}</span>
                  </div>
                  {a.note && (
                    <div style={{ 
                      fontSize: '13px', 
                      color: 'var(--text-muted)', 
                      marginTop: '12px', 
                      padding: '8px 12px', 
                      background: 'var(--bg)', 
                      borderRadius: 'var(--r-sm)',
                      border: '1px solid var(--border)',
                      fontStyle: 'italic'
                    }}>
                      {a.note}
                    </div>
                  )}
                </div>
                {(a.status !== 'cancelled' && a.status !== 'delayed') && (
                  <button 
                    className="btn btn-danger-soft" 
                    style={{ padding: '8px 16px', fontSize: '13px', marginLeft: '24px' }} 
                    onClick={() => cancel(a.id)}
                  >
                    Cancelar
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
};
