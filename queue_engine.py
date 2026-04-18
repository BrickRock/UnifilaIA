from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from models import PacienteFormado, EstadoAtencion, TurnoSimplificado

# ── Carga del modelo (una sola vez al importar el módulo) ──────────────────
import joblib, os

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_consultas.joblib")

try:
    _rf_model = joblib.load(_MODEL_PATH)
except FileNotFoundError:
    # GAP: el modelo no existe todavía (p.ej. primer deploy antes de entrenar).
    # Solución futura: entrenar en CI o exponer endpoint POST /admin/entrenar.
    _rf_model = None


class QueueEngine:
    # Minutos por paciente cuando no hay datos históricos ni modelo disponible
    MINUTOS_POR_PACIENTE = 15.0

    # Buffer de seguridad restado a la hora sugerida de arribo
    BUFFER_MINUTOS = 15.0

    @staticmethod
    def predict_duracion(
        preventiva: int,
        mas_de_un_sintoma: int,
        adulto: int,
        comorbilidad: int,
        tiene_laboratorio: int,
        es_seguimiento: int,
        num_consulta_turno: int,
    ) -> Optional[float]:
        """
        Predice la duración de la consulta usando el RandomForest entrenado.

        GAP — features faltantes en el schema actual vs columnas del modelo:
          · es_primera_vez : no se recopila en TurnoCreate → se asume 0 (no es primera vez).
            Impacto: el modelo podría sub/sobreestimar en primeras consultas.
            Fix: agregar es_primera_vez a TurnoCreate y TurnoSimplificado.

          · medico_id : no existe en el flujo de registro simplificado.
            Impacto: el modelo usa medico_id como feature importante (distintos médicos
            tienen tiempos distintos); fijarlo en 1 introduce sesgo.
            Fix: agregar Medico model + relación con TurnoSimplificado, o reentrenar
            sin medico_id si no se va a recopilar.

          · Mismatch de nombres columna → modelo (al entrenar el CSV):
              preventiva        → consulta_preventiva
              mas_de_un_sintoma → mas_de_1_sintoma
              adulto            → es_adulto
            El mapeo aquí es manual; si se reentena el modelo con nuevos nombres
            este mapeo debe actualizarse o el DataFrame debe usar los nombres del CSV.

          · num_consulta_turno se calcula como posición global en la cola, no por
            consultorio. Si hay múltiples consultorios el número inflará la estimación.
            Fix: filtrar por id_consultorio al contar.
        """
        if _rf_model is None:
            return None

        import pandas as pd

        features = pd.DataFrame([{
            "es_primera_vez":      0,          # GAP: hardcoded, ver notas arriba
            "consulta_preventiva": preventiva,  # nombre renombrado para el modelo
            "mas_de_1_sintoma":    mas_de_un_sintoma,
            "es_adulto":           adulto,
            "comorbilidad":        comorbilidad,
            "tiene_laboratorio":   tiene_laboratorio,
            "es_seguimiento":      es_seguimiento,
            "medico_id":           1,           # GAP: hardcoded, ver notas arriba
            "num_consulta_turno":  num_consulta_turno,
        }])

        return float(_rf_model.predict(features)[0])

    @classmethod
    def get_estimated_wait_time(cls, session: Session, id_consultorio: Optional[int] = None) -> float:
        """
        Suma las duraciones estimadas de todos los pacientes EN_ESPERA.
        Si no hay registros con duración estimada, usa MINUTOS_POR_PACIENTE × n_pacientes.

        GAP: TurnoSimplificado y PacienteFormado son entidades separadas.
        Este método solo suma TurnoSimplificado.duracion_estimada_minutos.
        Si el registro fue creado por /pacientes/presencial (PacienteFormado),
        no se considera aquí. Fix: unificar o sumar ambas tablas.
        """
        query = select(func.sum(TurnoSimplificado.duracion_estimada_minutos)).where(
            TurnoSimplificado.duracion_estimada_minutos.isnot(None)
        )
        suma_estimada = session.execute(query).scalar()

        if suma_estimada:
            return float(suma_estimada)

        # Cold start: no hay estimaciones previas → conteo × default
        conteo = session.execute(
            select(func.count(TurnoSimplificado.id))
        ).scalar() or 0
        return conteo * cls.MINUTOS_POR_PACIENTE

    @classmethod
    def calcular_hora_arribo(cls, session: Session, id_consultorio: Optional[int] = None) -> dict:
        """
        Retorna la hora sugerida de arribo:
            hora_actual + suma_tiempos_previos - BUFFER_MINUTOS
        """
        tiempo_espera = cls.get_estimated_wait_time(session, id_consultorio)
        tiempo_ajustado = max(0.0, tiempo_espera - cls.BUFFER_MINUTOS)
        hora_sugerida = datetime.now() + timedelta(minutes=tiempo_ajustado)
        return {
            "tiempo_espera_total_minutos": round(tiempo_espera, 1),
            "buffer_aplicado_minutos": cls.BUFFER_MINUTOS,
            "hora_sugerida_arribo": hora_sugerida.isoformat(),
        }

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
