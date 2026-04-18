import React, { useEffect, useState } from 'react';
import { PATH } from '../api';

interface QueuePageProps {
  user: any;
  onLeave: () => void;
  horaArribo?: string;       // ISO string del backend
  duracionMinutos?: number;
  sumaMinutos?: number;
}

function formatHHMM(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function addMinutes(iso: string, mins: number) {
  const d = new Date(new Date(iso).getTime() + mins * 60000);
  return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
}

export const QueuePage: React.FC<QueuePageProps> = ({
  onLeave, horaArribo, duracionMinutos, sumaMinutos
}: QueuePageProps) => {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [minutosRestantes, setMinutosRestantes] = useState<number>(999);

  // Calcular y actualizar minutos restantes cada 30s
  useEffect(() => {
    if (!horaArribo) return;
    const update = () => {
      const diff = (new Date(horaArribo).getTime() - Date.now()) / 60000;
      setMinutosRestantes(Math.max(0, Math.round(diff)));
    };
    update();
    const t = setInterval(update, 30000);
    return () => clearInterval(t);
  }, [horaArribo]);

  useEffect(() => {
    const fetchQueue = async () => {
      try {
        const res = await fetch(`${PATH}/atencion/cola`);
        if (res.ok) setQueue(await res.json());
      } catch (e) {
        console.error('Error fetching queue', e);
      } finally {
        setLoading(false);
      }
    };
    fetchQueue();
    const interval = setInterval(fetchQueue, 10000);
    return () => clearInterval(interval);
  }, []);

  const position = queue.findIndex(q => q.id === (window as any).activeQueueId) + 1;
  const urgent = minutosRestantes <= 60 && horaArribo !== undefined;

  const horaInicio = horaArribo ? formatHHMM(horaArribo) : '--:--';
  const horaFin    = horaArribo && duracionMinutos ? addMinutes(horaArribo, duracionMinutos) : '--:--';
  const esperaReal = sumaMinutos !== undefined ? Math.max(0, Math.round(sumaMinutos - 15)) : null;

  return (
    <main style={{ maxWidth: '600px', margin: '0 auto', padding: '60px 24px' }} className="animate-in">
      {/* Banner de alerta cuando queda menos de 1 hora */}
      {urgent && (
        <div style={{
          background: minutosRestantes <= 15 ? 'rgba(220,38,38,0.08)' : 'rgba(234,179,8,0.1)',
          border: `1.5px solid ${minutosRestantes <= 15 ? '#dc2626' : '#ca8a04'}`,
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          animation: minutosRestantes <= 15 ? 'pulse 1.5s infinite' : 'none',
        }}>
          <span style={{ fontSize: '24px' }}>{minutosRestantes <= 15 ? '🚨' : '⚠️'}</span>
          <div>
            <div style={{
              fontWeight: '700',
              fontSize: '14px',
              color: minutosRestantes <= 15 ? '#dc2626' : '#92400e',
            }}>
              {minutosRestantes <= 15
                ? '¡Dirígete a la clínica ahora!'
                : `Preséntate pronto — faltan ${minutosRestantes} minutos`}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Tu horario de arribo es a las {horaInicio}
            </div>
          </div>
        </div>
      )}

      <div
        className="card"
        style={{
          textAlign: 'center',
          padding: '48px 32px',
          boxShadow: urgent
            ? `0 0 0 2px ${minutosRestantes <= 15 ? '#dc2626' : '#ca8a04'}, var(--shadow-md)`
            : 'var(--shadow-md)',
          transition: 'box-shadow 0.3s',
        }}
      >
        <div style={{
          width: '80px', height: '80px',
          background: urgent ? (minutosRestantes <= 15 ? 'rgba(220,38,38,0.08)' : 'rgba(234,179,8,0.1)') : 'var(--bg)',
          borderRadius: '24px', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: '32px', margin: '0 auto 32px',
          transition: 'background 0.3s',
        }}>
          {urgent ? (minutosRestantes <= 15 ? '🏃' : '⏰') : '⏳'}
        </div>

        <h2 style={{ fontSize: '32px', marginBottom: '16px', letterSpacing: '-0.03em' }}>
          Lugar Reservado
        </h2>
        <p className="text-muted" style={{ fontSize: '16px', marginBottom: '40px' }}>
          {loading
            ? 'Calculando tu posición...'
            : `Hay ${queue.length} persona${queue.length !== 1 ? 's' : ''} en espera.`}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div style={{ background: 'var(--bg)', padding: '24px', borderRadius: 'var(--r)', border: '1px solid var(--border)' }}>
            <p style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
              Posición
            </p>
            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text)' }}>
              #{position > 0 ? position : 1}
            </div>
          </div>

          <div style={{ background: 'var(--bg)', padding: '24px', borderRadius: 'var(--r)', border: '1px solid var(--border)' }}>
            <p style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
              Espera Est.
            </p>
            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text)' }}>
              {esperaReal !== null ? `${esperaReal} min` : '—'}
            </div>
          </div>
        </div>

        {/* Tarjeta de minutos restantes */}
        {horaArribo && (
          <div style={{
            background: 'var(--bg)', padding: '16px', borderRadius: 'var(--r)',
            border: '1px solid var(--border)', marginBottom: '16px',
          }}>
            <p style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '6px' }}>
              Tiempo para presentarse
            </p>
            <div style={{
              fontSize: '22px', fontWeight: '800',
              color: minutosRestantes <= 15 ? '#dc2626' : minutosRestantes <= 60 ? '#ca8a04' : 'var(--text)',
            }}>
              {minutosRestantes > 0 ? `${minutosRestantes} min` : 'Ahora'}
            </div>
          </div>
        )}

        {/* Franja horaria */}
        <div style={{
          background: urgent
            ? (minutosRestantes <= 15 ? 'rgba(220,38,38,0.06)' : 'rgba(234,179,8,0.08)')
            : 'var(--green-lt)',
          padding: '20px',
          borderRadius: 'var(--r)',
          marginBottom: '40px',
          border: `1px solid ${urgent ? (minutosRestantes <= 15 ? '#dc2626' : '#ca8a04') : 'var(--green)'}`,
          transition: 'all 0.3s',
        }}>
          <p style={{ margin: 0, fontWeight: '600', color: urgent ? (minutosRestantes <= 15 ? '#dc2626' : '#92400e') : 'var(--green)' }}>
            Tu horario: {horaInicio} – {horaFin}
          </p>
          {duracionMinutos && (
            <p style={{ margin: '4px 0 0', fontSize: '12px', color: 'var(--text-muted)' }}>
              Consulta estimada: {Math.round(duracionMinutos)} min
            </p>
          )}
        </div>

        <button
          className="btn btn-danger-soft"
          style={{ width: '100%', padding: '16px', fontSize: '15px' }}
          onClick={onLeave}
        >
          Abandonar Fila
        </button>

        <p style={{ marginTop: '32px', fontSize: '13px' }} className="text-muted">
          Preséntate 5 minutos antes. Al salir perderás tu lugar de forma permanente.
        </p>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      `}</style>
    </main>
  );
};
