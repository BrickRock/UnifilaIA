import { useState, useEffect } from "react";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Navbar from "./components/Navbar";
import { api } from "./services/api";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Cargar sesión
    const savedUser = localStorage.getItem("unifila_user");
    if (savedUser) setUser(JSON.parse(savedUser));
    
    // Cargar preferencia de tema
    const savedTheme = localStorage.getItem("unifila_theme");
    if (savedTheme === "dark") setIsDarkMode(true);

    loadInitialData();
  }, []);

  useEffect(() => {
    // Aplicar clase al body para el tema
    if (isDarkMode) {
      document.body.classList.add("dark-mode");
      localStorage.setItem("unifila_theme", "dark");
    } else {
      document.body.classList.remove("dark-mode");
      localStorage.setItem("unifila_theme", "light");
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => setIsDarkMode(!isDarkMode);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const data = await api.getPatients();
      setPatients(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => setUser(userData);
  const handleLogout = async () => {
    await api.logout();
    setUser(null);
  };

  const addPatient = async (name, vitals) => {
    try {
      const newPatient = await api.addPatient(name, vitals);
      setPatients(prev => [...prev, newPatient]);
    } catch (err) {
      alert("Error al registrar paciente.");
    }
  };

  const prioritizePatient = async (patientId) => {
    try {
      await api.prioritizePatient(patientId);
      setPatients(prev => {
        const index = prev.findIndex(p => p.id === patientId);
        if (index === -1) return prev;
        const newPatients = [...prev];
        const [patient] = newPatients.splice(index, 1);
        return [patient, ...newPatients];
      });
    } catch (err) {
      alert("Error al priorizar paciente.");
    }
  };

  const cancelPatient = async (patientId) => {
    if (window.confirm("¿Está seguro de que desea cancelar la espera de este paciente?")) {
      try {
        await api.updatePatientStatus(patientId, "Cancelado");
        setPatients(prev => prev.filter(p => p.id !== patientId));
      } catch (err) {
        alert("Error al cancelar paciente.");
      }
    }
  };

  const removePatientFromList = async (patientId) => {
    try {
      await api.updatePatientStatus(patientId, "En consulta");
      setPatients(prev => prev.filter(p => p.id !== patientId));
    } catch (err) {
      console.error("Error al actualizar paciente");
    }
  };

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!user) return <Login onLogin={handleLogin} />;

  return (
    <div className={`app-wrapper ${isDarkMode ? 'dark-mode' : ''}`}>
      <Navbar 
        waitCount={patients.length} 
        user={user} 
        onLogout={handleLogout}
        isDarkMode={isDarkMode}
        toggleDarkMode={toggleDarkMode}
      />
      <Home 
        patients={patients} 
        addPatient={addPatient} 
        prioritizePatient={prioritizePatient}
        cancelPatient={cancelPatient}
        removePatientFromList={removePatientFromList} 
      />
    </div>
  );
}

export default App;