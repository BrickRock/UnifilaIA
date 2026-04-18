from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, or_, and_
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

    # Verificar que el paciente no esté ya en cola
    if payload.nss:
        existente = session.execute(
            select(TurnoSimplificado).where(TurnoSimplificado.nss == payload.nss)
        ).scalar_one_or_none()
        if existente:
            raise HTTPException(status_code=409, detail="Ya tienes un turno activo en la unifila.")

    # 1. Capturar suma de tiempos ANTES de insertar al nuevo paciente
    suma_anteriores = QueueEngine.get_suma_tiempos_cola(session)

    # 2. Posición en cola para la predicción
    num_consulta_turno = (
        session.execute(select(func.count(TurnoSimplificado.id))).scalar() or 0
    ) + 1

    # 3. Predecir duración con el RandomForest
    duracion_estimada = QueueEngine.predict_duracion(
        preventiva=payload.preventiva,
        mas_de_un_sintoma=payload.mas_de_un_sintoma,
        adulto=payload.adulto,
        comorbilidad=payload.comorbilidad,
        tiene_laboratorio=payload.tiene_laboratorio,
        es_seguimiento=payload.es_seguimiento,
        num_consulta_turno=num_consulta_turno,
    )

    # 4. Score = suma de factores de riesgo
    score = (
        payload.preventiva + payload.mas_de_un_sintoma + payload.adulto +
        payload.comorbilidad + payload.tiene_laboratorio + payload.es_seguimiento
    )

    # 5. Insertar turno con duración estimada
    nuevo_turno = TurnoSimplificado(
        **payload.model_dump(),
        score=score,
        duracion_estimada_minutos=duracion_estimada,
    )
    session.add(nuevo_turno)
    session.commit()

    # 6. Calcular hora sugerida: ahora + suma_anteriores - buffer
    arribo = QueueEngine.calcular_hora_arribo(suma_anteriores)

    return {
        "id": nuevo_turno.id,
        "score": score,
        "duracion_estimada_minutos": round(duracion_estimada, 1) if duracion_estimada else None,
        **arribo,
    }


@router.get("/estado/{nss}", status_code=200)
def estado_paciente(nss: str, session: Session = Depends(get_db)):
    turno = session.execute(
        select(TurnoSimplificado).where(TurnoSimplificado.nss == nss)
    ).scalar_one_or_none()

    if not turno:
        raise HTTPException(status_code=404, detail="No tienes turno activo.")

    # "Adelante" = mayor score, o mismo score pero id menor (llegó antes)
    condicion_adelante = or_(
        TurnoSimplificado.score > turno.score,
        and_(TurnoSimplificado.score == turno.score, TurnoSimplificado.id < turno.id)
    )

    adelante = session.execute(
        select(func.count(TurnoSimplificado.id)).where(condicion_adelante)
    ).scalar() or 0
    posicion = adelante + 1

    cola_adelante = session.execute(
        select(TurnoSimplificado).where(condicion_adelante)
    ).scalars().all()

    if cola_adelante:
        duraciones = [t.duracion_estimada_minutos or QueueEngine.MINUTOS_POR_PACIENTE for t in cola_adelante]
        suma_adelante = sum(duraciones)
    else:
        suma_adelante = 0.0

    arribo = QueueEngine.calcular_hora_arribo(suma_adelante)

    return {
        "id": turno.id,
        "score": turno.score,
        "posicion": posicion,
        "duracion_estimada_minutos": round(turno.duracion_estimada_minutos, 1) if turno.duracion_estimada_minutos else None,
        **arribo,
    }


@router.get("/cola", status_code=200)
def listar_cola(session: Session = Depends(get_db)):
    cola = session.query(TurnoSimplificado).order_by(TurnoSimplificado.score.desc(), TurnoSimplificado.id.asc()).all()
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
