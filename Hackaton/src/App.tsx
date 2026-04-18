import React, { useState, useEffect } from 'react';
import { Topbar } from './components/Topbar';
import { LoginPage } from './components/LoginPage';
import { RegisterPage } from './components/RegisterPage';
import { HomePage } from './components/HomePage';
import { QueuePage } from './components/QueuePage';
import { ConfirmModal } from './components/ConfirmModal';
import { readJWT } from './utils';
import { PATH } from './api';
import './index.css';

const App: React.FC = () => {
  const [page, setPage] = useState('login');
  const [user, setUser] = useState<any>(null);
  const [activeQueueAppt, setActiveQueueAppt] = useState<any | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('mc_theme') || 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('mc_theme', theme);
  }, [theme]);

  useEffect(() => {
    const tok = localStorage.getItem('mc_token');
    if (!tok) return;
    const p = readJWT(tok);
    if (!p || !p.exp || p.exp * 1000 <= Date.now()) {
      localStorage.removeItem('mc_token');
      return;
    }
    const restoredUser = { nss: p.nss || p.sub, nombre: p.nombre, name: p.nombre, id: p.id, role: p.role };
    setUser(restoredUser);

    // Verificar si ya tiene turno activo en la unifila
    fetch(`${PATH}/atencion/estado/${p.nss || p.sub}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) {
          (window as any).activeQueueId = data.id;
          setActiveQueueAppt({
            id: data.id,
            score: data.score,
            horaArribo: data.hora_sugerida_arribo,
            duracionMinutos: data.duracion_estimada_minutos,
            sumaMinutos: data.suma_tiempos_anteriores_min,
          });
          setPage('queue');
        } else {
          setPage('home');
        }
      })
      .catch(() => setPage('home'));
  }, []);

  const logout = () => {
    localStorage.removeItem('mc_token');
    setUser(null);
    setPage('login');
    setActiveQueueAppt(null);
  };

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  const handleJoinQueue = async (currentUser = user) => {
    const payload = {
      nss: currentUser?.nss || null,
      preventiva: 0,
      mas_de_un_sintoma: 1,
      adulto: 1,
      comorbilidad: 0,
      tiene_laboratorio: 0,
      es_seguimiento: 0,
    };

    try {
      const res = await fetch(`${PATH}/atencion/registrar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.status === 409) {
        // Ya tiene turno — obtener estado actual y mostrar QueuePage
        const estado = await fetch(`${PATH}/atencion/estado/${currentUser?.nss}`);
        if (estado.ok) {
          const data = await estado.json();
          (window as any).activeQueueId = data.id;
          setActiveQueueAppt({
            id: data.id,
            score: data.score,
            horaArribo: data.hora_sugerida_arribo,
            duracionMinutos: data.duracion_estimada_minutos,
            sumaMinutos: data.suma_tiempos_anteriores_min,
          });
          setPage('queue');
        }
        return;
      }

      if (res.ok) {
        const data = await res.json();
        (window as any).activeQueueId = data.id;
        setActiveQueueAppt({
          id: data.id,
          score: data.score,
          horaArribo: data.hora_sugerida_arribo,
          duracionMinutos: data.duracion_estimada_minutos,
          sumaMinutos: data.suma_tiempos_anteriores_min,
        });
        setPage('queue');
      } else {
        alert('Error al unirse a la fila');
      }
    } catch (e) {
      console.error('Queue error', e);
      alert('Error de conexión con el servidor');
    }
  };

  const handleLeaveQueue = () => {
    setActiveQueueAppt(null);
    setPage('home');
  };

  if (!user && (page === 'login' || page === 'register')) {
    return page === 'login' ? (
      <LoginPage setUser={setUser} setPage={setPage} />
    ) : (
      <RegisterPage setPage={setPage} />
    );
  }

  let content;
  if (!user) content = <LoginPage setUser={setUser} setPage={setPage} />;
  else if (page === 'home') content = (
    <HomePage 
      user={user} 
      setPage={(p) => p === 'queue' && !activeQueueAppt ? handleJoinQueue() : setPage(p)} 
      activeAppt={activeQueueAppt}
      onLeaveQueue={() => setIsConfirmOpen(true)}
    />
  );
  else if (page === 'queue') content = (
    <QueuePage
      nss={user?.nss}
      onLeave={() => setIsConfirmOpen(true)}
      horaArribo={activeQueueAppt?.horaArribo}
      duracionMinutos={activeQueueAppt?.duracionMinutos}
      sumaMinutos={activeQueueAppt?.sumaMinutos}
    />
  );
  else content = <HomePage user={user} setPage={setPage} activeAppt={activeQueueAppt} onLeaveQueue={() => setIsConfirmOpen(true)} />;

  return (
    <div className="app-shell">
      <Topbar 
        page={page} 
        setPage={(p) => p === 'queue' && !activeQueueAppt ? handleJoinQueue() : setPage(p)} 
        user={user} 
        logout={logout} 
        theme={theme}
        toggleTheme={toggleTheme}
      />
      {content}
      <ConfirmModal 
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleLeaveQueue}
        title="¿Abandonar fila?"
        message="Estás a punto de cancelar tu cita actual y perder tu lugar en la fila virtual."
      />
    </div>
  );
};

export default App;
