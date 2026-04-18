import React from 'react';

interface TopbarProps {
  page: string;
  setPage: (page: string) => void;
  user: any;
  logout: () => void;
  theme: string;
  toggleTheme: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ page, setPage, user, logout, theme, toggleTheme }) => {
  return (
    <div className="topbar">
      <div className="topbar-inner">
        <button className="logo" onClick={() => setPage(user ? 'home' : 'login')}>
          <img 
            src="/IMSS_Logosímbolo.png" 
            alt="Logo" 
            style={{ width: '32px', height: 'auto' }} 
          />
          Unifila IMSS
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {user && (
            <div className="nav-pills" style={{ marginRight: '8px' }}>
              <button className={`nav-pill ${page === 'home' ? 'on' : ''}`} onClick={() => setPage('home')}>
                Inicio
              </button>
            </div>
          )}
          
          <button 
            className="theme-toggle" 
            style={{ 
              width: '40px', 
              height: '40px', 
              background: 'transparent', 
              border: '1px solid var(--border)',
              borderRadius: '10px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px',
              color: 'var(--text)'
            }} 
            onClick={toggleTheme} 
            title="Cambiar tema"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginLeft: '8px' }}>
              <div style={{ textAlign: 'right', display: 'none', md: 'block' }}>
                <div style={{ fontSize: '13px', fontWeight: '600' }}>{user.name.split(' ')[0]}</div>
              </div>
              <button 
                className="btn btn-ghost" 
                style={{ padding: '8px 16px', fontSize: '13px' }} 
                onClick={logout}
              >
                Salir
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 8, marginLeft: '8px' }}>
              <button className={`nav-pill ${page === 'login' ? 'on' : ''}`} onClick={() => setPage('login')}>Entrar</button>
              <button 
                className="btn btn-primary" 
                style={{ padding: '8px 16px', fontSize: '13px' }} 
                onClick={() => setPage('register')}
              >
                Empezar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
