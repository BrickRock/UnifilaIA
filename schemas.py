from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from models import TipoConsulta
from datetime import datetime, date
from typing import Optional, List
from models import TipoConsulta, EstadoAtencion, TriageLevel


class PacienteBase(BaseModel):
    curp: str = Field(..., min_length=18, max_length=18)
    nss: Optional[str] = Field(None, min_length=11, max_length=11, description="NSS de 11 dígitos")
    nombre_completo: str
    fecha_nacimiento: date
    sexo: Optional[str] = None
    es_cronico: bool = False

class PacienteCreate(PacienteBase):
    es_cronico_general: bool = False

class TurnoCreate(BaseModel):
    preventiva: int = Field(..., ge=0, le=1)
    mas_de_un_sintoma: int = Field(..., ge=0, le=1)
    adulto: int = Field(..., ge=0, le=1)
    comorbilidad: int = Field(..., ge=0, le=1)
    tiene_laboratorio: int = Field(..., ge=0, le=1)
    es_seguimiento: int = Field(..., ge=0, le=1)
