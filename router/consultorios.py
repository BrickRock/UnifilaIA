from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from models import Consultorio, PacienteFormado
from schemas import AsignarConsultorioRequest

router = APIRouter(prefix="/consultorios", tags=["Consultorios"])


def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


@router.get("", status_code=200)
def listar_consultorios(session: Session = Depends(get_db)):
    consultorios = session.query(Consultorio).all()
    return [
        {"id_consultorio": c.id_consultorio, "numero": c.numero, "piso": c.piso}
        for c in consultorios
    ]


@router.post("/asignar", status_code=200)
def asignar_consultorio(body: AsignarConsultorioRequest, session: Session = Depends(get_db)):
    turno = session.get(PacienteFormado, body.id_turno_dia)
    if not turno:
        raise HTTPException(status_code=404, detail=f"Turno {body.id_turno_dia} no encontrado.")

    consultorio = session.get(Consultorio, body.id_consultorio)
    if not consultorio:
        raise HTTPException(status_code=404, detail=f"Consultorio {body.id_consultorio} no encontrado.")

    try:
        turno.id_consultorio = body.id_consultorio
        session.commit()
        return {
            "mensaje": "Consultorio asignado correctamente.",
            "id_turno_dia": body.id_turno_dia,
            "consultorio": consultorio.numero,
            "piso": consultorio.piso,
        }
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al asignar consultorio: {e}")
