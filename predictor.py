"""
Ejecutar UNA VEZ dentro del contenedor para generar modelo_consultas.joblib:
    docker exec <container> python predictor.py
"""
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import joblib

df = pd.read_csv("dataset_consultas.csv")

# Renombrar columnas del CSV a los nombres que usa TurnoCreate en el front
df = df.rename(columns={
    "consulta_preventiva": "preventiva",
    "mas_de_1_sintoma":    "mas_de_un_sintoma",
    "es_adulto":           "adulto",
})

# Features exactas que el front envía + posición en cola calculada en runtime
FEATURES = [
    "preventiva",
    "mas_de_un_sintoma",
    "adulto",
    "comorbilidad",
    "tiene_laboratorio",
    "es_seguimiento",
    "num_consulta_turno",
]

X = df[FEATURES]
y = df["duracion_minutos"]

rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf.fit(X, y)

joblib.dump(rf, "modelo_consultas.joblib")
print(f"Modelo guardado. Features: {FEATURES}")
print(f"R² en entrenamiento: {rf.score(X, y):.3f}")
