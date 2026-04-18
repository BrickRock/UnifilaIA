import React, { useEffect, useState } from 'react';
import { PATH } from '../api';

interface QueuePageProps {
  user: any;
  onLeave: () => void;
  timeRange: string;
}

export const QueuePage: React.FC<QueuePageProps> = ({ user, onLeave, timeRange }) => {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQueue = async () => {
      try {
        const res = await fetch(`${PATH}/atencion/cola`);
        if (res.ok) {
          const data = await res.json();
          setQueue(data);
        }
      } catch (e) {
        console.error("Error fetching queue", e);
      } finally {
        setLoading(false);
      }
    };

    fetchQueue();
    const interval = setInterval(fetchQueue, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const position = queue.findIndex(q => q.id === (window as any).activeQueueId) + 1;

  return (
    <main style={{ maxWidth: '600px', margin: '0 auto', padding: '60px 24px' }} className="animate-in">
      <div className="card" style={{ textAlign: 'center', padding: '48px 32px', boxShadow: 'var(--shadow-md)' }}>
        <div style={{ 
          width: '80px', height: '80px', background: 'var(--bg)', 
          borderRadius: '24px', display: 'flex', alignItems: 'center', 
          justifyContent: 'center', fontSize: '32px', margin: '0 auto 32px'
        }}>
          ⏳
        </div>
        
        <h2 style={{ fontSize: '32px', marginBottom: '16px', letterSpacing: '-0.03em' }}>Lugar Reservado</h2>
        <p className="text-muted" style={{ fontSize: '16px', marginBottom: '40px' }}>
          {loading ? 'Calculando tu posición...' : `Hay ${queue.length} personas en espera. Eres el siguiente en la lista.`}
        </p>
        
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '16px',
          marginBottom: '40px'
        }}>
          <div style={{ 
            background: 'var(--bg)', 
            padding: '24px', 
            borderRadius: 'var(--r)', 
            border: '1px solid var(--border)'
          }}>
            <p style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
              Posición
            </p>
            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text)' }}>
              #{position > 0 ? position : '1'}
            </div>
          </div>

          <div style={{ 
            background: 'var(--bg)', 
            padding: '24px', 
            borderRadius: 'var(--r)', 
            border: '1px solid var(--border)'
          }}>
            <p style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
              Espera Est.
            </p>
            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text)' }}>
              15 min
            </div>
          </div>
        </div>

        <div style={{ 
          background: 'var(--green-lt)', 
          padding: '20px', 
          borderRadius: 'var(--r)', 
          marginBottom: '40px',
          border: '1px solid var(--green)'
        }}>
           <p style={{ margin: 0, color: 'var(--green)', fontWeight: '600' }}>
            Tu horario: {timeRange}
           </p>
        </div>

        <button 
          className="btn btn-danger-soft" 
          style={{ width: '100%', padding: '16px', fontSize: '15px' }} 
          onClick={onLeave}
        >
          Abandonar Fila
        </button>
        
        <p style={{ marginTop: '32px', fontSize: '13px' }} className="text-muted">
          Presentate 5 minutos antes. Al salir perderás tu lugar actual de forma permanente.
        </p>
      </div>
    </main>
  );
};
