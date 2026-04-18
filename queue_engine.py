from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from models import PacienteFormado, EstadoAtencion


class QueueEngine:
    MINUTOS_POR_PACIENTE = 15.0

    @staticmethod
    def calculate_priority_score(score: int, hora_llegada: datetime, desplazamientos: int = 0) -> float:
        minutos_esperando = (datetime.now() - hora_llegada).total_seconds() / 60
        return (score * 10) - minutos_esperando + (desplazamientos * 15)

    @classmethod
    def get_estimated_wait_time(cls, session: Session, id_consultorio: Optional[int] = None) -> float:
        query = select(func.count(PacienteFormado.id_turno_dia)).where(
            PacienteFormado.estado_atencion == EstadoAtencion.EN_ESPERA
        )
        if id_consultorio is not None:
            query = query.where(PacienteFormado.id_consultorio == id_consultorio)

        pacientes_en_espera = session.execute(query).scalar() or 0
        return pacientes_en_espera * cls.MINUTOS_POR_PACIENTE

    @staticmethod
    def check_no_show_ttl(session: Session) -> int:
        limite = datetime.now() - timedelta(minutes=5)
        ausentes = session.scalars(
            select(PacienteFormado).where(
                PacienteFormado.estado_atencion == EstadoAtencion.LLAMADO,
                PacienteFormado.hora_llamado < limite
            )
        ).all()
        for p in ausentes:
            p.estado_atencion = EstadoAtencion.NO_PRESENTADO
        session.commit()
        return len(ausentes)
