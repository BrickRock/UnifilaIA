import React, { useState, useEffect, useCallback } from 'react';
import { BRANCHES, SPECS } from '../data';
import { getSlots, nextFreeDay } from '../utils';

interface BookModalProps {
  user: any;
  onClose: () => void;
  onSave: () => void;
}

export const BookModal: React.FC<BookModalProps> = ({ user, onClose, onSave }) => {
  const today = new Date().toISOString().split('T')[0];
  const [spec, setSpec] = useState(SPECS[0]);
  const [branch, setBranch] = useState(user.branch || BRANCHES[0].name);
  const [date, setDate] = useState(today);
  const [slots, setSlots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [nextDay, setNextDay] = useState<any>(null);

  const bObj = BRANCHES.find((b) => b.name === branch) || BRANCHES[0];

  const fetchSlots = useCallback(() => {
    setLoading(true);
    setSelected(null);
    setNextDay(null);
    setTimeout(() => {
      const s = getSlots(date, bObj.id);
      setSlots(s);
      if (!s.some((x) => !x.busy)) {
        const nxt = nextFreeDay(date, bObj.id);
        if (nxt) setNextDay(nxt);
      }
      setLoading(false);
    }, Math.random() * 300 + 300);
  }, [date, bObj.id]);

  useEffect(() => {
    fetchSlots();
  }, [fetchSlots]);

  const jumpToNext = () => {
    if (!nextDay) return;
    setDate(nextDay.date);
  };

  const confirm = () => {
    if (!selected) return;
    const key = 'mc_appts_' + user.curp;
    const appts = JSON.parse(localStorage.getItem(key) || '[]');
    appts.unshift({ id: Date.now(), spec, date, time: selected.time, consultory: selected.consultory, status: 'pending', branch, note: '' });
    localStorage.setItem(key, JSON.stringify(appts));
    onSave();
    onClose();
  };

  return (
    <div className="modal-bg" onClick={(ev) => { if (ev.target === ev.currentTarget) onClose(); }}>
      <div className="modal" style={{ maxWidth: '540px' }}>
        <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>Nueva Cita</h2>
        <p className="text-muted" style={{ fontSize: '15px', marginBottom: '32px' }}>
          Selecciona los detalles para tu próxima consulta médica.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="fg">
            <label>Especialidad</label>
            <select value={spec} onChange={(ev) => setSpec(ev.target.value)}>
              {SPECS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="fg">
            <label>Sucursal</label>
            <select value={branch} onChange={(ev) => setBranch(ev.target.value)}>
              {BRANCHES.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
            </select>
          </div>
        </div>
        
        <div className="fg">
          <label>Fecha de Consulta</label>
          <input type="date" value={date} min={today} onChange={(ev) => setDate(ev.target.value)} />
        </div>

        <div style={{ margin: '24px 0 12px', fontSize: '13px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Horarios Disponibles
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center' }}>
            <span className="text-muted">Cargando disponibilidad...</span>
          </div>
        ) : nextDay ? (
          <div className="card" style={{ background: 'var(--bg)', textAlign: 'center', marginBottom: '24px' }}>
            <p style={{ fontSize: '14px', marginBottom: '16px' }}>
              No hay horarios para esta fecha. Próximo disponible: <strong>{nextDay.date}</strong>
            </p>
            <button className="btn btn-ghost" style={{ background: 'var(--bg-card)' }} onClick={jumpToNext}>
              Ir al {nextDay.date}
            </button>
          </div>
        ) : (
          <div className="avail-grid">
            {slots.map((sl, i) => (
              <div
                key={i}
                className={`slot ${sl.busy ? 'busy' : 'free'} ${selected && selected.time === sl.time ? ' sel' : ''}`}
                onClick={() => !sl.busy && setSelected(sl)}
              >
                <div className="slot-time">{sl.time}</div>
                <div className="slot-lbl">{sl.busy ? 'Ocupado' : 'Cons. ' + sl.consultory}</div>
              </div>
            ))}
          </div>
        )}

        {selected && (
          <div style={{ 
            background: 'var(--green-lt)', 
            color: 'var(--green)', 
            padding: '12px 16px', 
            borderRadius: 'var(--r-sm)', 
            fontSize: '14px', 
            fontWeight: '600',
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            ✓ Seleccionado: {selected.time} (Cons. {selected.consultory})
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
          <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose}>Cancelar</button>
          <button className="btn btn-primary" style={{ flex: 2 }} onClick={confirm} disabled={!selected || loading}>
            Confirmar Cita
          </button>
        </div>
      </div>
    </div>
  );
};
