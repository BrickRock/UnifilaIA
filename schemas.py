from pydantic import BaseModel, Field

class TurnoCreate(BaseModel):
    preventiva: int = Field(..., ge=0, le=1)
    mas_de_un_sintoma: int = Field(..., ge=0, le=1)
    adulto: int = Field(..., ge=0, le=1)
    comorbilidad: int = Field(..., ge=0, le=1)
    tiene_laboratorio: int = Field(..., ge=0, le=1)
    es_seguimiento: int = Field(..., ge=0, le=1)
