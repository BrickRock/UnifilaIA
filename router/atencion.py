from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
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

    # Posición en la cola para que el modelo la use como feature
    num_consulta_turno = (session.execute(select(func.count(TurnoSimplificado.id))).scalar() or 0) + 1

    duracion_estimada = QueueEngine.predict_duracion(
        preventiva=payload.preventiva,
        mas_de_un_sintoma=payload.mas_de_un_sintoma,
        adulto=payload.adulto,
        comorbilidad=payload.comorbilidad,
        tiene_laboratorio=payload.tiene_laboratorio,
        es_seguimiento=payload.es_seguimiento,
        num_consulta_turno=num_consulta_turno,
    )

    nuevo_turno = TurnoSimplificado(
        **payload.model_dump(),
        score=score,
        duracion_estimada_minutos=duracion_estimada,
    )
    session.add(nuevo_turno)
    session.commit()

    arribo = QueueEngine.calcular_hora_arribo(session)

    return {
        "mensaje": "Turno registrado.",
        "id": nuevo_turno.id,
        "score": score,
        "duracion_estimada_minutos": round(duracion_estimada, 1) if duracion_estimada else None,
        **arribo,
    }


@router.get("/cola", status_code=200)
def listar_cola(session: Session = Depends(get_db)):
    cola = session.query(TurnoSimplificado).order_by(TurnoSimplificado.score.desc()).all()
    return [
        {
            "id": t.id,
            "score": t.score,
            "adulto": t.adulto,
            "comorbilidad": t.comorbilidad,
            "duracion_estimada_minutos": t.duracion_estimada_minutos,
        }
        for t in cola
    ]


@router.delete("/{turno_id}", status_code=200)
def cancelar_turno(turno_id: int, session: Session = Depends(get_db)):
    turno = session.query(TurnoSimplificado).filter(TurnoSimplificado.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado.")
    session.delete(turno)
    session.commit()
    return {"mensaje": f"Turno {turno_id} cancelado."}
