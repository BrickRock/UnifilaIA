from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from models import TipoConsulta


class PacienteCreate(BaseModel):
    nss: str = Field(min_length=11, max_length=11, description="NSS de 11 dígitos")
    nombre_completo: str = Field(max_length=150)
    fecha_nacimiento: date
    sexo: Optional[str] = Field(default=None, max_length=1, description="M o F")
    es_cronico_general: bool = False


class PacienteFormadoCreate(BaseModel):
    id_paciente: int
    id_consultorio: int
    telefono: int
    tipo_consulta: TipoConsulta
    indicador_cronicidad: bool
    edad_al_momento: int = Field(gt=0)
