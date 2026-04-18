import { useState } from "react";
import { api } from "../services/api";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const user = await api.login(username, password);
      onLogin(user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="card login-card" style={{ maxWidth: '600px', padding: '6rem' }}>
        <div style={{ textAlign: "center", marginBottom: "5rem" }}>
          <h1 style={{ color: "var(--primary)", fontSize: "1.5rem", fontWeight: "950", letterSpacing: "0.25em" }}>
            UNIFILA CLINIC
          </h1>
          <div style={{ width: '40px', height: '2px', background: 'var(--accent)', margin: '1.5rem auto' }}></div>
          <p style={{ color: "var(--text-muted)", fontSize: "0.75rem", fontWeight: "800", textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            Acceso Autorizado al Sistema
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-field" style={{ marginBottom: "3rem" }}>
            <label>USUARIO</label>
            <input
              type="text"
              placeholder="Admin ID"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-field" style={{ marginBottom: "3rem" }}>
            <label>CONTRASEÑA</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div style={{ color: "var(--danger)", marginBottom: "3rem", fontSize: "0.7rem", textAlign: "center", fontWeight: "900", textTransform: 'uppercase' }}>
              {error}
            </div>
          )}

          <button 
            className="btn-primary" 
            type="submit" 
            style={{ width: "100%", padding: "1.5rem" }}
            disabled={loading}
          >
            {loading ? "VERIFICANDO..." : "AUTENTICAR"}
          </button>
        </form>

        <p style={{ marginTop: '5rem', fontSize: '0.65rem', color: 'var(--text-muted)', textAlign: 'center', fontWeight: '700', opacity: 0.5 }}>
          CLÍNICA DIGITAL — SISTEMA DE GESTIÓN DE ALTA DISPONIBILIDAD
        </p>
      </div>
    </div>
  );
}

export default Login;