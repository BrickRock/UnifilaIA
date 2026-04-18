from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, Enum as SQLEnum, func, CHAR, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class TipoConsulta(str, Enum):
    PRESENCIAL = "Presencial"
    EN_LINEA = "En_Linea"

class EstadoAtencion(str, Enum):
    EN_ESPERA = "En_Espera"
    LLAMADO = "Llamado"
    EN_ATENCION = "En_Atencion"
    FINALIZADO = "Finalizado"
    CANCELADO = "Cancelado"
    NO_PRESENTADO = "No_Presentado"

class TriageLevel(int, Enum):
    ROJO = 1       # Inmediato
    NARANJA = 2    # Emergencia
    AMARILLO = 3   # Urgente
    VERDE = 4      # Urgencia Menor
    AZUL = 5       # No Urgente

class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente: Mapped[int] = mapped_column(Integer, primary_key=True)
    curp: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_nacimiento: Mapped[Date] = mapped_column(Date, nullable=False)
    sexo: Mapped[Optional[str]] = mapped_column(CHAR(1))
    es_cronico: Mapped[bool] = mapped_column(Boolean, default=False)

    turnos: Mapped[list["Turno"]] = relationship(back_populates="paciente")

class Consultorio(Base):
    __tablename__ = "consultorio"
    id_consultorio: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[str] = mapped_column(String(10), unique=True)
    especialidad: Mapped[str] = mapped_column(String(50)) # Crucial para el tiempo estimado

class Turno(Base):
    __tablename__ = "turno"

    id_turno: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_paciente: Mapped[int] = mapped_column(ForeignKey("paciente.id_paciente"))
    id_consultorio: Mapped[int] = mapped_column(ForeignKey("consultorio.id_consultorio"))
    
    tipo_consulta: Mapped[TipoConsulta] = mapped_column(SQLEnum(TipoConsulta))
    triage: Mapped[TriageLevel] = mapped_column(Integer, default=TriageLevel.VERDE)
    
    # Lógica de Swap y Prioridad
    desplazamientos: Mapped[int] = mapped_column(Integer, default=0)
    prioridad_ajustada: Mapped[float] = mapped_column(Float) # Score dinámico para el algoritmo
    
    hora_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    hora_llamado: Mapped[Optional[datetime]] = mapped_column(DateTime)
    hora_fin: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    estado: Mapped[EstadoAtencion] = mapped_column(SQLEnum(EstadoAtencion), default=EstadoAtencion.EN_ESPERA)

    paciente: Mapped["Paciente"] = relationship(back_populates="turnos")

class HistorialAtencion(Base):
    """Tabla para entrenamiento del modelo ML"""
    __tablename__ = "historial_atencion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    especialidad: Mapped[str] = mapped_column(String(50))
    triage: Mapped[int] = mapped_column(Integer)
    hora_dia: Mapped[int] = mapped_column(Integer)
    dia_semana: Mapped[int] = mapped_column(Integer)
    duracion_minutos: Mapped[float] = mapped_column(Float)
