from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from models import TipoConsulta, EstadoAtencion, TriageLevel

class PacienteBase(BaseModel):
    curp: str = Field(..., min_length=18, max_length=18)
    nombre_completo: str
    fecha_nacimiento: date
    sexo: Optional[str] = None
    es_cronico: bool = False

class PacienteCreate(PacienteBase):
    pass

class TurnoCreate(BaseModel):
    curp: str
    id_consultorio: int
    tipo_consulta: TipoConsulta
    triage: TriageLevel

class TurnoResponse(BaseModel):
    id_turno: int
    nombre_paciente: str
    triage: int
    estado: EstadoAtencion
    tiempo_espera_estimado: float
    posicion: int

    class Config:
        from_attributes = True
