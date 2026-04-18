from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import db
from models import Paciente
import schemas

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

@router.post("/", response_model=schemas.PacienteBase)
def registrar_paciente(paciente: schemas.PacienteCreate, session: Session = Depends(get_db)):
    # Validar si ya existe la CURP
    db_paciente = session.query(Paciente).filter(Paciente.curp == paciente.curp).first()
    if db_paciente:
        raise HTTPException(status_code=400, detail="El paciente con esta CURP ya existe")
    
    nuevo_paciente = Paciente(**paciente.model_dump())
    session.add(nuevo_paciente)
    session.commit()
    session.refresh(nuevo_paciente)
    return nuevo_paciente

@router.get("/{curp}", response_model=schemas.PacienteBase)
def obtener_paciente(curp: str, session: Session = Depends(get_db)):
    paciente = session.query(Paciente).filter(Paciente.curp == curp).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente
