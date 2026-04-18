from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import db
from models import TurnoSimplificado
from schemas import TurnoCreate
from queue_engine import QueueEngine
from utils import ESTADOS_UNIFILA

router = APIRouter(prefix="/atencion", tags=["Atención Simplificada"])

_estado_sistema = ESTADOS_UNIFILA.NORMAL


def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


@router.post("/registrar", status_code=201)
def registrar_turno(payload: TurnoCreate, session: Session = Depends(get_db)):
    if _estado_sistema == ESTADOS_UNIFILA.SATURADO:
        raise HTTPException(status_code=503, detail="Sistema saturado. No se aceptan nuevos turnos.")

    score = (
        payload.preventiva +
        payload.mas_de_un_sintoma +
        payload.adulto +
        payload.comorbilidad +
        payload.tiene_laboratorio +
        payload.es_seguimiento
    )

    nuevo_turno = TurnoSimplificado(**payload.model_dump(), score=score)
    session.add(nuevo_turno)
    session.commit()

    tiempo_estimado = QueueEngine.get_estimated_wait_time(session)
    hora_sugerida = datetime.now() + timedelta(minutes=tiempo_estimado)

    return {
        "mensaje": "Turno registrado.",
        "id": nuevo_turno.id,
        "score": score,
        "tiempo_estimado_minutos": tiempo_estimado,
        "hora_sugerida_llegada": hora_sugerida.isoformat(),
    }


@router.get("/cola", status_code=200)
def listar_cola(session: Session = Depends(get_db)):
    cola = session.query(TurnoSimplificado).order_by(TurnoSimplificado.score.desc()).all()
    return [
        {"id": t.id, "score": t.score, "adulto": t.adulto, "comorbilidad": t.comorbilidad}
        for t in cola
    ]
    return cola

@router.delete("/{turno_id}")
def cancelar_turno(turno_id: int, session: Session = Depends(get_db)):
    turno = session.query(TurnoSimplificado).filter(TurnoSimplificado.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    session.delete(turno)
    session.commit()
    return {"mensaje": "Turno cancelado"}
