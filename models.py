from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, Enum as SQLEnum, func, CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

class RegistrarPacienteRequest(BaseModel):
    nombre: str
    apellido: str
    curp: str

class RegistroPresencialRequest(BaseModel):
    nss: str
    nombre_completo: str
    fecha_nacimiento: str  # Formato YYYY-MM-DD
    sexo: str
    telefono: int
    id_consultorio: int
    tipo_consulta: TipoConsulta
    es_cronico: bool = False


from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class TurnoSimplificado(Base):
    __tablename__ = "turno_simplificado"

    id = Column(Integer, primary_key=True)
    preventiva = Column(Integer, nullable=False)
    mas_de_un_sintoma = Column(Integer, nullable=False)
    adulto = Column(Integer, nullable=False)
    comorbilidad = Column(Integer, nullable=False)
    tiene_laboratorio = Column(Integer, nullable=False)
    es_seguimiento = Column(Integer, nullable=False)
    
    # El score se puede calcular al momento de insertar o guardar
    score = Column(Integer, nullable=False)
