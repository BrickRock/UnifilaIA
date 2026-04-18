from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import db
from models import Paciente, Turno, EstadoAtencion, Consultorio
from queue_engine import QueueEngine
from predictor import predictor
import schemas

router = APIRouter(prefix="/atencion", tags=["Atención y Colas"])

def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

@router.post("/registrar", response_model=schemas.TurnoResponse)
def registrar_paciente(payload: schemas.TurnoCreate, session: Session = Depends(get_db)):
    # 1. Verificar si el paciente existe
    paciente = session.query(Paciente).filter(Paciente.curp == payload.curp).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no registrado. Registre sus datos personales primero.")

    # 2. Crear el turno
    nuevo_turno = Turno(
        id_paciente=paciente.id_paciente,
        id_consultorio=payload.id_consultorio,
        tipo_consulta=payload.tipo_consulta,
        triage=payload.triage,
        estado=EstadoAtencion.EN_ESPERA,
        prioridad_ajustada=0.0 # Se calculará ahora
    )
    
    # 3. Lógica de Swap y Recálculo de Prioridades
    # Antes de añadirlo, actualizamos los scores de todos los que están esperando
    otros_en_espera = session.query(Turno).filter(
        Turno.id_consultorio == payload.id_consultorio,
        Turno.estado == EstadoAtencion.EN_ESPERA
    ).all()

    nuevo_turno.prioridad_ajustada = QueueEngine.calculate_priority_score(nuevo_turno)
    
    for t in otros_en_espera:
        old_priority = t.prioridad_ajustada
        t.prioridad_ajustada = QueueEngine.calculate_priority_score(t)
        # Si el nuevo paciente tiene menor score (más prioridad) y "salta" a alguien
        if nuevo_turno.prioridad_ajustada < t.prioridad_ajustada:
            t.desplazamientos += 1

    session.add(nuevo_turno)
    session.commit()
    session.refresh(nuevo_turno)

    # 4. Calcular tiempo estimado total
    tiempo_estimado = QueueEngine.get_estimated_wait_time(session, payload.id_consultorio)

    return {
        "id_turno": nuevo_turno.id_turno,
        "nombre_paciente": paciente.nombre_completo,
        "triage": nuevo_turno.triage,
        "estado": nuevo_turno.estado,
        "tiempo_espera_estimado": tiempo_estimado,
        "posicion": len(otros_en_espera) + 1
    }

@router.get("/cola/{id_consultorio}", response_model=list[schemas.TurnoResponse])
def ver_cola(id_consultorio: int, session: Session = Depends(get_db)):
    """
    Retorna la cola ordenada por prioridad dinámica.
    """
    cola = session.query(Turno).filter(
        Turno.id_consultorio == id_consultorio,
        Turno.estado == EstadoAtencion.EN_ESPERA
    ).order_by(Turno.prioridad_ajustada).all()

    resultado = []
    tiempo_acumulado = 0.0
    
    for i, t in enumerate(cola):
        duracion_estimada = predictor.predict_duration(t.triage, "General")
        tiempo_acumulado += duracion_estimada
        
        resultado.append({
            "id_turno": t.id_turno,
            "nombre_paciente": t.paciente.nombre_completo,
            "triage": t.triage,
            "estado": t.estado,
            "tiempo_espera_estimado": tiempo_acumulado,
            "posicion": i + 1
        })
    
    return resultado
