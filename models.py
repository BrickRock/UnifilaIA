from enum import Enum
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, Float,
    ForeignKey, Enum as SQLEnum, Text, func, CHAR
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property


# ── Enums ──────────────────────────────────────────────────────────────────

class TipoConsulta(str, Enum):
    PRIMERA_VEZ   = "Primera_Vez"
    SEGUIMIENTO   = "Seguimiento"
    URGENCIA      = "Urgencia"
    PROCEDIMIENTO = "Procedimiento"


class EstadoAtencion(str, Enum):
    EN_ESPERA     = "En_Espera"
    LLAMADO       = "Llamado"
    EN_ATENCION   = "En_Atencion"
    FINALIZADO    = "Finalizado"
    CANCELADO     = "Cancelado"
    NO_PRESENTADO = "No_Presentado"


class TriageLevel(int, Enum):
    ROJO     = 1
    NARANJA  = 2
    AMARILLO = 3
    VERDE    = 4
    AZUL     = 5


# ── Base SQLAlchemy ────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Modelos SQLAlchemy ─────────────────────────────────────────────────────

class Consultorio(Base):
    __tablename__ = "consultorio"

    id_consultorio: Mapped[int]           = mapped_column(Integer, primary_key=True)
    numero:         Mapped[str]           = mapped_column(String(10), unique=True, nullable=False)
    piso:           Mapped[Optional[int]] = mapped_column(Integer)

    turnos: Mapped[list["PacienteFormado"]] = relationship(back_populates="consultorio")


class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente:        Mapped[int]           = mapped_column(Integer, primary_key=True)
    nss:                Mapped[str]           = mapped_column(String(11), unique=True, nullable=False)
    nombre_completo:    Mapped[str]           = mapped_column(String(150), nullable=False)
    fecha_nacimiento:   Mapped[date]          = mapped_column(Date, nullable=False)
    sexo:               Mapped[Optional[str]] = mapped_column(CHAR(1))
    es_cronico_general: Mapped[bool]          = mapped_column(Boolean, default=False)

    turnos: Mapped[list["PacienteFormado"]] = relationship(back_populates="paciente")


class PacienteFormado(Base):
    __tablename__ = "paciente_formado"

    id_turno_dia:         Mapped[int]                = mapped_column(Integer, primary_key=True)
    id_paciente:          Mapped[int]                = mapped_column(ForeignKey("paciente.id_paciente"), nullable=False)
    id_consultorio:       Mapped[Optional[int]]      = mapped_column(ForeignKey("consultorio.id_consultorio"), nullable=True)
    telefono:             Mapped[int]                = mapped_column(Integer, nullable=False)
    tipo_consulta:        Mapped[TipoConsulta]       = mapped_column(SQLEnum(TipoConsulta), nullable=False)
    indicador_cronicidad: Mapped[bool]               = mapped_column(Boolean, nullable=False)
    edad_al_momento:      Mapped[int]                = mapped_column(Integer, nullable=False)
    hora_llegada:         Mapped[datetime]           = mapped_column(DateTime, server_default=func.now())
    hora_llamado:         Mapped[Optional[datetime]] = mapped_column(DateTime)
    hora_fin_atencion:    Mapped[Optional[datetime]] = mapped_column(DateTime)
    estado_atencion:      Mapped[EstadoAtencion]     = mapped_column(
        SQLEnum(EstadoAtencion), default=EstadoAtencion.EN_ESPERA
    )

    paciente:    Mapped["Paciente"]              = relationship(back_populates="turnos")
    consultorio: Mapped[Optional["Consultorio"]] = relationship(back_populates="turnos")
    consulta:    Mapped[Optional["Consulta"]]    = relationship(back_populates="turno", uselist=False)

    @hybrid_property
    def tiempo_espera_minutos(self) -> float:
        if self.hora_llamado and self.hora_llegada:
            return (self.hora_llamado - self.hora_llegada).total_seconds() / 60
        return 0.0

    @hybrid_property
    def tiempo_atencion_minutos(self) -> float:
        if self.hora_fin_atencion and self.hora_llamado:
            return (self.hora_fin_atencion - self.hora_llamado).total_seconds() / 60
        return 0.0


class TurnoSimplificado(Base):
    __tablename__ = "turno_simplificado"

    id:                       Mapped[int]            = mapped_column(Integer, primary_key=True)
    preventiva:               Mapped[int]            = mapped_column(Integer, nullable=False)
    mas_de_un_sintoma:        Mapped[int]            = mapped_column(Integer, nullable=False)
    adulto:                   Mapped[int]            = mapped_column(Integer, nullable=False)
    comorbilidad:             Mapped[int]            = mapped_column(Integer, nullable=False)
    tiene_laboratorio:        Mapped[int]            = mapped_column(Integer, nullable=False)
    es_seguimiento:           Mapped[int]            = mapped_column(Integer, nullable=False)
    score:                    Mapped[int]            = mapped_column(Integer, nullable=False)
    duracion_estimada_minutos: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class Consulta(Base):
    __tablename__ = "consulta"

    id_consulta:      Mapped[int]           = mapped_column(Integer, primary_key=True)
    id_turno_dia:     Mapped[int]           = mapped_column(ForeignKey("paciente_formado.id_turno_dia"), nullable=False)
    diagnostico:      Mapped[str]           = mapped_column(Text, nullable=False)
    duracion_minutos: Mapped[float]         = mapped_column(Float, nullable=False)
    hora_inicio:      Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    hora_fin:         Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    notas:            Mapped[Optional[str]] = mapped_column(Text)

    turno: Mapped["PacienteFormado"] = relationship(back_populates="consulta")


# ── Pydantic Request Models ────────────────────────────────────────────────

class RegistroPresencialRequest(BaseModel):
    nss:              str
    nombre_completo:  str
    fecha_nacimiento: str           # YYYY-MM-DD
    sexo:             str
    telefono:         int
    id_consultorio:   Optional[int] = None
    tipo_consulta:    TipoConsulta
    es_cronico:       bool = False
