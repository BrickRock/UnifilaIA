/**
 * SERVICIO DE API - UNIFILA HEALTH
 */
import PATH from "../api";

export const api = {
  /**
   * Autenticación Mock (Se puede conectar al back si hay endpoint de login)
   */
  async login(username, password) {
    await new Promise(resolve => setTimeout(resolve, 800));
    if (username === "admin" && password === "admin123") {
      const user = { username: "Admin", role: "Administrador", token: "fake-jwt-token" };
      localStorage.setItem("unifila_user", JSON.stringify(user));
      return user;
    } else {
      throw new Error("Credenciales inválidas. Intenta con admin / admin123");
    }
  },

  async logout() {
    localStorage.removeItem("unifila_user");
    return true;
  },

  /**
   * Obtener todos los pacientes (de la cola de atención)
   */
  async getPatients() {
    try {
      const response = await fetch(`${PATH}/atencion/cola`);
      if (!response.ok) throw new Error("Error al obtener pacientes");
      const data = await response.json();
      // Mapeamos para que coincida con lo que espera el front (name, etc)
      // Como TurnoSimplificado no tiene nombre, pondremos uno genérico o ID
      return data.map(p => ({
        id: p.id,
        name: `Paciente ${p.id}`,
        status: "En espera",
        vitals: p
      }));
    } catch (error) {
      console.error("API GET Error:", error);
      throw error;
    }
  },

  /**
   * Registrar un nuevo paciente con signos vitales
   */
  async addPatient(name, vitals) {
    try {
      const response = await fetch(`${PATH}/atencion/registrar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(vitals)
      });
      if (!response.ok) throw new Error("Error al registrar paciente");
      const data = await response.json();
      return { 
        id: data.id, 
        name: name || `Paciente ${data.id}`, 
        status: "En espera", 
        vitals 
      };
    } catch (error) {
      console.error("API POST Error:", error);
      throw error;
    }
  },

  /**
   * Priorizar paciente
   */
  async prioritizePatient(id) {
    try {
      // Por ahora el back no tiene un endpoint de "priorizar" explícito
      // pero el orden se da por el score.
      return true;
    } catch (error) {
      console.error("API Prioritize Error:", error);
      throw error;
    }
  },

  /**
   * Actualizar estado del paciente (Cancelar o Asignar)
   */
  async updatePatientStatus(id, status) {
    try {
      if (status === "Cancelado" || status === "En consulta") {
        const response = await fetch(`${PATH}/atencion/${id}`, {
          method: 'DELETE'
        });
        if (!response.ok) throw new Error("Error al actualizar estado en el servidor");
        return await response.json();
      }
      return { id, status };
    } catch (error) {
      console.error("API DELETE/PATCH Error:", error);
      throw error;
    }
  }
};
