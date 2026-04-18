from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils import ESTADOS_UNIFILA
from models import Paciente, PacienteFormado
from schemas import PacienteCreate, PacienteFormadoCreate
from database import db
from router import atencion, pacientes

app = FastAPI(title="UnifilaIA API")

# Incluir los nuevos routers
app.include_router(atencion.router)
app.include_router(pacientes.router)

ESTADO = ESTADOS_UNIFILA.NORMAL.value

@app.get("/health")
def health_check():
    try:
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB no disponible: {e}")

ESTADO = ESTADOS_UNIFILA.NORMAL.value

@app.get("/")
def read_root():
    return {"message": "Bienvenido a UnifilaIA API"}

@app.get("/estado_unifila")
def get_status():
    return {"estado": ESTADO}


@app.post("/pacientes", status_code=201)
def registrar_paciente(body: PacienteCreate):
    if ESTADO == ESTADOS_UNIFILA.SATURADO.value:
        raise HTTPException(status_code=400, detail="Sistema saturado no se aceptan nuevos pacientes en unifila")
    session = db.get_session()
    try:
        paciente = Paciente(**body.model_dump())
        session.add(paciente)
        session.commit()
        session.refresh(paciente)
        return {"mensaje": "Paciente registrado", "id_paciente": paciente.id_paciente, "status" : ESTADO}
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un paciente con ese NSS ({body.nss})."
        )
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar paciente: {e}")
    finally:
        session.close()


@app.post("/pacientes-formados", status_code=201)
def registrar_paciente_formado(body: PacienteFormadoCreate):
    session = db.get_session()
    try:
        formado = PacienteFormado(**body.model_dump())
        session.add(formado)
        session.commit()
        session.refresh(formado)
        return {"mensaje": "Paciente formado registrado", "id_turno_dia": formado.id_turno_dia}
    except IntegrityError as e:
        session.rollback()
        orig = str(e.orig)
        if "id_paciente" in orig:
            detail = f"No existe un paciente con id {body.id_paciente}."
        elif "id_consultorio" in orig:
            detail = f"No existe un consultorio con id {body.id_consultorio}."
        else:
            detail = "Violación de integridad en la BD."
        raise HTTPException(status_code=409, detail=detail)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar paciente formado: {e}")
    finally:
        session.close()
