from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime, timedelta
from database import db
from models import Consulta, PacienteFormado, EstadoAtencion
from schemas import ConsultaCreate
from queue_engine import QueueEngine

router = APIRouter(prefix="/consultas", tags=["Consultas"])


def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


@router.post("", status_code=201)
def registrar_consulta(body: ConsultaCreate, session: Session = Depends(get_db)):
    turno = session.get(PacienteFormado, body.id_turno_dia)
    if not turno:
        raise HTTPException(status_code=404, detail=f"Turno {body.id_turno_dia} no encontrado.")
    if turno.estado_atencion == EstadoAtencion.FINALIZADO:
        raise HTTPException(status_code=409, detail="El turno ya tiene una consulta registrada.")

    try:
        consulta = Consulta(**body.model_dump())
        turno.estado_atencion = EstadoAtencion.FINALIZADO
        turno.hora_fin_atencion = body.hora_fin
        session.add(consulta)
        session.commit()
        session.refresh(consulta)
        return {"mensaje": "Consulta registrada.", "id_consulta": consulta.id_consulta}
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"Error de integridad: {e.orig}")
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar consulta: {e}")


@router.get("/horario", status_code=200)
def obtener_horario(
    id_consultorio: int = Query(..., description="ID del consultorio"),
    session: Session = Depends(get_db),
):
    tiempo_espera = QueueEngine.get_estimated_wait_time(session, id_consultorio)
    ahora = datetime.now()
    slot_disponible = ahora + timedelta(minutes=tiempo_espera)

    return {
        "id_consultorio": id_consultorio,
        "hora_actual": ahora.isoformat(),
        "tiempo_espera_estimado_minutos": tiempo_espera,
        "proximo_slot_disponible": slot_disponible.isoformat(),
        "dia": slot_disponible.strftime("%A %d/%m/%Y"),
        "hora": slot_disponible.strftime("%H:%M"),
    }
