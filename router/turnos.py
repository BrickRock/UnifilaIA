from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import db
from models import PacienteFormado, EstadoAtencion
from services import QueueService

router = APIRouter(prefix="/turnos", tags=["Turnos"])

ESTADOS_FINALES = {EstadoAtencion.FINALIZADO, EstadoAtencion.CANCELADO, EstadoAtencion.NO_PRESENTADO}


def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


@router.post("/{id_turno}/cancelar", status_code=200)
def cancelar_turno(id_turno: int, session: Session = Depends(get_db)):
    turno = session.get(PacienteFormado, id_turno)
    if not turno:
        raise HTTPException(status_code=404, detail=f"Turno {id_turno} no encontrado.")
    if turno.estado_atencion in ESTADOS_FINALES:
        raise HTTPException(
            status_code=409,
            detail=f"Turno ya en estado final: {turno.estado_atencion.value}. No se puede cancelar."
        )
    exito = QueueService.cancelar_turno(id_turno)
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo cancelar el turno.")
    return {"mensaje": f"Turno {id_turno} cancelado correctamente."}


@router.get("/{id_turno}/estado", status_code=200)
def consultar_estado(id_turno: int):
    resultado = QueueService.obtener_posicion_cola(id_turno)
    if resultado is None:
        raise HTTPException(status_code=404, detail=f"Turno {id_turno} no encontrado.")
    return resultado
