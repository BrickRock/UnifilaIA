from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from models import TipoConsulta, EstadoAtencion


class PacienteCreate(BaseModel):
    nss:                str  = Field(min_length=11, max_length=11, description="NSS de 11 dígitos")
    nombre_completo:    str  = Field(max_length=150)
    fecha_nacimiento:   date
    sexo:               Optional[str] = Field(default=None, max_length=1, description="M o F")
    es_cronico_general: bool = False


class PacienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_paciente:        int
    nss:                str
    nombre_completo:    str
    fecha_nacimiento:   date
    sexo:               Optional[str]
    es_cronico_general: bool


class PacienteFormadoCreate(BaseModel):
    id_paciente:          int
    id_consultorio:       Optional[int] = None
    telefono:             int
    tipo_consulta:        TipoConsulta
    indicador_cronicidad: bool
    edad_al_momento:      int = Field(gt=0)


class TurnoCreate(BaseModel):
    preventiva:        int = Field(..., ge=0, le=1)
    mas_de_un_sintoma: int = Field(..., ge=0, le=1)
    adulto:            int = Field(..., ge=0, le=1)
    comorbilidad:      int = Field(..., ge=0, le=1)
    tiene_laboratorio: int = Field(..., ge=0, le=1)
    es_seguimiento:    int = Field(..., ge=0, le=1)


class AsignarConsultorioRequest(BaseModel):
    id_turno_dia:   int
    id_consultorio: int


class ConsultaCreate(BaseModel):
    id_turno_dia:     int
    diagnostico:      str
    duracion_minutos: float = Field(gt=0)
    hora_inicio:      datetime
    hora_fin:         datetime
    notas:            Optional[str] = None
