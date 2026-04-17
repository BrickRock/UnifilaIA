
from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, Enum as SQLEnum, func, CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

class Base(DeclarativeBase):
    pass

class TipoConsulta(str, Enum):
    PRIMERA_VEZ = "Primera_Vez"
    SEGUIMIENTO = "Seguimiento"
    URGENCIA = "Urgencia"
    PROCEDIMIENTO = "Procedimiento"

class EstadoAtencion(str, Enum):
    EN_ESPERA = "En_Espera"
    LLAMADO = "Llamado"
    EN_ATENCION = "En_Atencion"
    FINALIZADO = "Finalizado"
    CANCELADO = "Cancelado"

class Consultorio(Base):
    __tablename__ = "consultorio"
    
    id_consultorio: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    piso: Mapped[Optional[int]] = mapped_column(Integer)
    
    turnos: Mapped[list["PacienteFormado"]] = relationship(back_populates="consultorio")

class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente: Mapped[int] = mapped_column(Integer, primary_key=True)
    nss: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_nacimiento: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    sexo: Mapped[Optional[str]] = mapped_column(CHAR(1))
    es_cronico_general: Mapped[bool] = mapped_column(Boolean, default=False)

    turnos: Mapped[list["PacienteFormado"]] = relationship(back_populates="paciente")

class PacienteFormado(Base):
    __tablename__ = "paciente_formado"

    id_turno_dia: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_paciente: Mapped[int] = mapped_column(ForeignKey("paciente.id_paciente"), nullable=False)
    id_consultorio: Mapped[int] = mapped_column(ForeignKey("consultorio.id_consultorio"), nullable=False)
    telefono: Mapped[int] = mapped_column(Integer, nullable=False)
    
    tipo_consulta: Mapped[TipoConsulta] = mapped_column(SQLEnum(TipoConsulta), nullable=False)
    indicador_cronicidad: Mapped[bool] = mapped_column(Boolean, nullable=False)
    edad_al_momento: Mapped[int] = mapped_column(Integer, nullable=False)
    
    hora_llegada: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    hora_llamado: Mapped[Optional[datetime]] = mapped_column(DateTime)
    hora_fin_atencion: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    estado_atencion: Mapped[EstadoAtencion] = mapped_column(
        SQLEnum(EstadoAtencion), default=EstadoAtencion.EN_ESPERA
    )

    # Relaciones
    paciente: Mapped["Paciente"] = relationship(back_populates="turnos")
    consultorio: Mapped["Consultorio"] = relationship(back_populates="turnos")

    @hybrid_property
    def tiempo_espera_minutos(self) -> float:
        if self.hora_llamado and self.hora_llegada:
            delta = self.hora_llamado - self.hora_llegada
            return delta.total_seconds() / 60
        return 0.0

    @hybrid_property
    def tiempo_atencion_minutos(self) -> float:
        if self.hora_fin_atencion and self.hora_llamado:
            delta = self.hora_fin_atencion - self.hora_llamado
            return delta.total_seconds() / 60
        return 0.0
