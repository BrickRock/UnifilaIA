from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import db
from models import TurnoSimplificado
import schemas

router = APIRouter(prefix="/atencion", tags=["Atención Simplificada"])

def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

@router.post("/registrar")
def registrar_turno(payload: schemas.TurnoCreate, session: Session = Depends(get_db)):
    # Cálculo simple de score: sumatoria de factores de riesgo
    # Puedes ajustar esta lógica según tus necesidades
    score = (
        payload.preventiva +
        payload.mas_de_un_sintoma +
        payload.adulto +
        payload.comorbilidad +
        payload.tiene_laboratorio +
        payload.es_seguimiento
    )
    
    nuevo_turno = TurnoSimplificado(
        **payload.model_dump(),
        score=score
    )
    
    session.add(nuevo_turno)
    session.commit()
    return {"mensaje": "Turno registrado", "id": nuevo_turno.id, "score": score}

@router.get("/cola")
def listar_cola(session: Session = Depends(get_db)):
    # Retorna la cola ordenada por score (mayor score = mayor prioridad)
    cola = session.query(TurnoSimplificado).order_by(TurnoSimplificado.score.desc()).all()
    return cola

@router.delete("/{turno_id}")
def cancelar_turno(turno_id: int, session: Session = Depends(get_db)):
    turno = session.query(TurnoSimplificado).filter(TurnoSimplificado.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    session.delete(turno)
    session.commit()
    return {"mensaje": "Turno cancelado"}
