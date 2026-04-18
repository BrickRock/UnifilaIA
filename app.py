from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from utils import ESTADOS_UNIFILA
from models import RegistrarPacienteRequest, PacienteFormado, EstadoAtencion, RegistroPresencialRequest
from database import db
from services import QueueService

app = FastAPI()


@app.get("/health")
def health_check():
    try:
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB no disponible: {e}")

ESTADO = ESTADOS_UNIFILA.NORMAL.value

pacientes_db: list[dict] = []


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/estado_unifila")
def get_status():
    """
    Retorna el estado actual de la unifila: NORMAL, SATURANDOSE o SATURADO.
    """
    return {"estado": ESTADO}


@app.post("/pacientes", status_code=200)
def registrar_paciente(body: RegistrarPacienteRequest):
    if ESTADO == ESTADOS_UNIFILA.SATURADO.value:
        raise HTTPException(status_code=503, detail="Unifila saturada, no se aceptan más pacientes.")

    paciente = {
        "id": len(pacientes_db) + 1,
        "nombre": body.nombre,
        "apellido": body.apellido,
        "curp": body.curp,
        "estado": EstadoAtencion.EN_ESPERA.value
    }
    pacientes_db.append(paciente)

    # TODO: persistir con db.get_session() cuando la BD esté levantada
    return {"mensaje": "Paciente registrado", "paciente": paciente}


@app.post("/pacientes/{id_turno}/cancelar", status_code=200)
def cancelar_paciente(id_turno: int):
    """
    Cancela un registro en la cola de atención por su ID.
    """
    for p in pacientes_db:
        if p["id"] == id_turno:
            p["estado"] = EstadoAtencion.CANCELADO.value
            break
            
    exito = QueueService.cancelar_turno(id_turno)
    if not exito:
        return {"mensaje": f"Turno {id_turno} cancelado en memoria"}
    
    return {"mensaje": f"Turno {id_turno} cancelado con éxito"}


@app.post("/mantenimiento/limpiar-espera-excesiva", status_code=200)
def limpiar_espera_excesiva(minutos: int = 60):
    """
    Busca y cancela automáticamente todos los turnos que excedan el tiempo de espera.
    """
    cancelados = QueueService.cancelar_por_tiempo_espera(minutos)
    return {
        "mensaje": "Limpieza de cola completada", 
        "total_cancelados": cancelados,
        "criterio_minutos_maximo": minutos
    }


@app.get("/pacientes/{id_turno}/estado", status_code=200)
def consultar_estado_lugar(id_turno: int):
    """
    Consulta la posición actual, personas por delante y tiempo estimado de espera.
    """
    resultado = QueueService.obtener_posicion_cola(id_turno)
    
    if resultado is None:
        # Respaldo para lista mock
        for p in pacientes_db:
            if p["id"] == id_turno:
                return {
                    "id": id_turno,
                    "nombre": p["nombre"],
                    "estado": p.get("estado", "En_Espera"),
                    "mensaje": "Datos desde memoria temporal"
                }
        raise HTTPException(status_code=404, detail="Turno no encontrado")
        
    return resultado


@app.post("/pacientes/presencial", status_code=201)
def registrar_presencial(body: RegistroPresencialRequest):
    """
    Registra a un paciente de manera presencial en la clínica.
    """
    try:
        nuevo_turno = QueueService.registrar_presencial(body)
        return {
            "mensaje": "Paciente registrado presencialmente",
            "id_turno": nuevo_turno.id_turno_dia,
            "paciente": body.nombre_completo,
            "consultorio": body.id_consultorio,
            "estado": nuevo_turno.estado_atencion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en registro presencial: {e}")
