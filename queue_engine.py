import os
import joblib
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from models import PacienteFormado, EstadoAtencion, TurnoSimplificado

# ── Modelo cargado una sola vez al importar ────────────────────────────────
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_consultas.joblib")

try:
    _rf_model = joblib.load(_MODEL_PATH)
except FileNotFoundError:
    _rf_model = None


class QueueEngine:
    BUFFER_MINUTOS       = 15.0
    MINUTOS_POR_PACIENTE = 15.0   # fallback cold-start

    # ── Predicción ─────────────────────────────────────────────────────────

    @staticmethod
    def predict_duracion(
        preventiva:        int,
        mas_de_un_sintoma: int,
        adulto:            int,
        comorbilidad:      int,
        tiene_laboratorio: int,
        es_seguimiento:    int,
        num_consulta_turno: int,
    ) -> Optional[float]:
        """
        Predice duración de consulta usando el RandomForest.
        Features = exactamente lo que el front envía + posición en cola.
        Retorna None si el modelo no está disponible.
        """
        if _rf_model is None:
            return None

        import pandas as pd
        features = pd.DataFrame([{
            "preventiva":         preventiva,
            "mas_de_un_sintoma":  mas_de_un_sintoma,
            "adulto":             adulto,
            "comorbilidad":       comorbilidad,
            "tiene_laboratorio":  tiene_laboratorio,
            "es_seguimiento":     es_seguimiento,
            "num_consulta_turno": num_consulta_turno,
        }])
        return float(_rf_model.predict(features)[0])

    # ── Cola ───────────────────────────────────────────────────────────────

    @classmethod
    def get_suma_tiempos_cola(cls, session: Session) -> float:
        """
        Suma las duraciones estimadas de todos los pacientes actualmente en cola.
        Si no hay estimaciones (cold start), usa MINUTOS_POR_PACIENTE × n_pacientes.
        """
        suma = session.execute(
            select(func.sum(TurnoSimplificado.duracion_estimada_minutos)).where(
                TurnoSimplificado.duracion_estimada_minutos.isnot(None)
            )
        ).scalar()

        if suma:
            return float(suma)

        # Cold start: no hay duraciones guardadas aún
        n = session.execute(select(func.count(TurnoSimplificado.id))).scalar() or 0
        return n * cls.MINUTOS_POR_PACIENTE

    @classmethod
    def calcular_hora_arribo(cls, suma_tiempos_anteriores: float) -> dict:
        """
        hora_sugerida = ahora + suma_tiempos_anteriores - BUFFER_MINUTOS

        El buffer cubre imprevistos (cancelaciones, ausencias, etc.).
        suma_tiempos_anteriores debe capturarse ANTES de insertar al nuevo paciente.
        """
        tiempo_ajustado = max(0.0, suma_tiempos_anteriores - cls.BUFFER_MINUTOS)
        hora_sugerida   = datetime.now(timezone.utc) + timedelta(minutes=tiempo_ajustado)
        return {
            "suma_tiempos_anteriores_min": round(suma_tiempos_anteriores, 1),
            "buffer_aplicado_min":         cls.BUFFER_MINUTOS,
            "hora_sugerida_arribo":        hora_sugerida.isoformat(),
        }

    # ── Mantenimiento ──────────────────────────────────────────────────────

    @staticmethod
    def check_no_show_ttl(session: Session) -> int:
        """Marca como NO_PRESENTADO a pacientes LLAMADOS sin presentarse en 5 min."""
        limite = datetime.now() - timedelta(minutes=5)
        ausentes = session.scalars(
            select(PacienteFormado).where(
                PacienteFormado.estado_atencion == EstadoAtencion.LLAMADO,
                PacienteFormado.hora_llamado    < limite,
            )
        ).all()
        for p in ausentes:
            p.estado_atencion = EstadoAtencion.NO_PRESENTADO
        session.commit()
        return len(ausentes)
