from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Turno, TriageLevel, EstadoAtencion, Consultorio, HistorialAtencion
from sqlalchemy import func

class QueueEngine:
    # Tiempos base por Triage (en minutos) - Estrategia Cold Start
    BASE_TIMES = {
        1: 5.0,   # Rojo: Atención inmediata (estabilización rápida o pase directo)
        2: 20.0,  # Naranja
        3: 30.0,  # Amarillo
        4: 15.0,  # Verde (consultas rápidas)
        5: 10.0   # Azul (recetas o temas simples)
    }

    @staticmethod
    def calculate_priority_score(turno: Turno) -> float:
        """
        Calcula el score de prioridad. A menor score, más prioridad.
        Considera: Triage, Tiempo de espera y penalización por desplazamientos.
        """
        ahora = datetime.now()
        minutos_esperando = (ahora - turno.hora_registro).total_seconds() / 60
        
        # El Triage es el factor más fuerte (100, 200, 300...)
        # Restamos los minutos esperando para que quien lleva más tiempo gane prioridad
        # Sumamos penalización por desplazamientos previos para evitar el "starvation"
        score = (turno.triage * 100) - minutos_esperando + (turno.desplazamientos * 15)
        return score

    @classmethod
    def get_estimated_wait_time(cls, session: Session, id_consultorio: int) -> float:
        """
        Suma los tiempos estimados de todos los pacientes delante en la cola.
        """
        # Fase 1: Intentar obtener promedio histórico real de la DB
        # Si no hay datos (Cold Start), usar BASE_TIMES
        count = session.query(func.count(HistorialAtencion.id)).scalar()
        
        pacientes_esperando = session.query(Turno).filter(
            Turno.id_consultorio == id_consultorio,
            Turno.estado == EstadoAtencion.EN_ESPERA
        ).order_by(Turno.prioridad_ajustada).all()

        total_wait = 0.0
        for p in pacientes_esperando:
            # Por ahora usamos tiempos base, en el futuro llamará al modelo ML
            total_wait += cls.BASE_TIMES.get(p.triage, 15.0)
            
        return total_wait

    @staticmethod
    def check_no_show_ttl(session: Session):
        """
        Regla de Ausentismo: TTL de 5 minutos para pacientes LLAMADOS.
        """
        limite_tolerancia = datetime.now() - timedelta(minutes=5)
        
        pacientes_ausentes = session.query(Turno).filter(
            Turno.estado == EstadoAtencion.LLAMADO,
            Turno.hora_llamado < limite_tolerancia
        ).all()

        for p in pacientes_ausentes:
            p.estado = EstadoAtencion.NO_PRESENTADO
            # Aquí se dispararía un evento de WebSocket para avisar el cambio
            
        session.commit()
