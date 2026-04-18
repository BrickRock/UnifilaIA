from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from models import Paciente, RegistroPresencialRequest
from schemas import PacienteCreate, PacienteResponse
from services import QueueService

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


@router.post("/", response_model=PacienteResponse, status_code=201)
def registrar_paciente(paciente: PacienteCreate, session: Session = Depends(get_db)):
    if session.query(Paciente).filter(Paciente.nss == paciente.nss).first():
        raise HTTPException(status_code=409, detail=f"Ya existe un paciente con NSS {paciente.nss}.")
    try:
        nuevo = Paciente(**paciente.model_dump())
        session.add(nuevo)
        session.commit()
        session.refresh(nuevo)
        return nuevo
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar paciente: {e}")


@router.get("/{nss}", response_model=PacienteResponse)
def obtener_paciente(nss: str, session: Session = Depends(get_db)):
    paciente = session.query(Paciente).filter(Paciente.nss == nss).first()
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con NSS {nss} no encontrado.")
    return paciente


@router.post("/presencial", status_code=201)
def registrar_presencial(body: RegistroPresencialRequest):
    try:
        turno = QueueService.registrar_presencial(body)
        return {
            "mensaje": "Paciente registrado presencialmente.",
            "id_turno_dia": turno.id_turno_dia,
            "estado": turno.estado_atencion,
        }
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Error de integridad: {e.orig}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en registro presencial: {e}")
