from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import joblib

df = pd.read_csv("dataset_consultas.csv")

X = df.drop(columns=["paciente_id", "duracion_minutos"])
y = df["duracion_minutos"]

rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf.fit(X, y)  # ← aquí ocurre TODO el aprendizaje
#pip install -U scikit-learns
joblib.dump(rf, "modelo_consultas.joblib")
