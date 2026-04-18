function Navbar({ waitCount, user, onLogout, isDarkMode, toggleDarkMode }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span>UNIFILA HEALTH</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        {/* Toggle de Tema */}
        <button 
          className="theme-toggle" 
          onClick={toggleDarkMode}
          title={isDarkMode ? "Modo Claro" : "Modo Oscuro"}
        >
          {isDarkMode ? "☀️" : "🌙"}
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="stat-badge">{waitCount}</span>
        </div>

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', borderLeft: '1px solid var(--border)', paddingLeft: '2rem' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.9rem', fontWeight: '800', color: 'var(--primary)' }}>{user.username}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{user.role}</div>
            </div>
            <button 
              className="btn-outline" 
              onClick={onLogout}
              style={{ padding: '0.5rem 0.75rem', fontSize: '0.8rem' }}
            >
              SALIR
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;