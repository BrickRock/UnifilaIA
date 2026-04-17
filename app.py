from fastapi import FastAPI, HTTPException
import random
from utils import ESTADOS_UNIFILA
from models import RegistrarPacienteRequest

app = FastAPI()

ESTADO = ESTADOS_UNIFILA.NORMAL.value

# Storage dummy en memoria
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
        Permite obtener el estado de la unifila 1 = CLOSED, 2= OPEN, 3= HALF-OPEN
    """
    return ESTADO


@app.post("/pacientes", status_code=200)
def registrar_paciente(body: RegistrarPacienteRequest):
    if ESTADO == ESTADOS_UNIFILA.SATURADO.value:
        raise HTTPException(status_code)
    paciente = {
        "id": len(pacientes_db) + 1,
        "nombre": body.nombre,
        "apellido": body.apellido,
        "curp": body.curp,
    }
    pacientes_db.append(paciente)
    return {"mensaje": "Paciente registrado", "paciente": paciente}