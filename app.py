from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from utils import ESTADOS_UNIFILA
from models import RegistrarPacienteRequest
from database import db

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
    }
    pacientes_db.append(paciente)

    # TODO: persistir con db.get_session() cuando la BD esté levantada
    return {"mensaje": "Paciente registrado", "paciente": paciente}
