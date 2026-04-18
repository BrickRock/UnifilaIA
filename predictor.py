import pandas as pd
import numpy as np
from datetime import datetime
# En producción: import xgboost as xgb

class WaitTimePredictor:
    def __init__(self):
        self.model = None # Se cargará cuando haya suficientes datos
        self.is_trained = False

    def _get_features(self, triage: int, especialidad: str):
        """Prepara las variables de entrada para el modelo"""
        ahora = datetime.now()
        features = {
            "triage": triage,
            "hour": ahora.hour,
            "day_of_week": ahora.weekday(),
            "is_weekend": 1 if ahora.weekday() >= 5 else 0,
            "month": ahora.month,
            # Podríamos agregar estacionalidad (ej: influenza en invierno)
            "is_flu_season": 1 if ahora.month in [11, 12, 1, 2] else 0
        }
        return features

    def predict_duration(self, triage: int, especialidad: str) -> float:
        """
        Predice cuánto durará la consulta. 
        Si no hay modelo entrenado, usa heurística experta.
        """
        if not self.is_trained:
            # Heurística experta (Cold Start)
            base_times = {1: 10, 2: 25, 3: 40, 4: 20, 5: 15}
            return float(base_times.get(triage, 20))
        
        # Lógica para cuando el modelo esté entrenado:
        # X = self._preprocess(self._get_features(triage, especialidad))
        # return self.model.predict(X)
        return 20.0 

# Singleton para uso en toda la app
predictor = WaitTimePredictor()
