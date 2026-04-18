from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from utils import ESTADOS_UNIFILA
from database import db
from router import atencion, pacientes

app = FastAPI(title="UnifilaIA API")

# Incluir los nuevos routers
app.include_router(atencion.router)
app.include_router(pacientes.router)

ESTADO = ESTADOS_UNIFILA.NORMAL.value

@app.get("/health")
def health_check():
    try:
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB no disponible: {e}")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a UnifilaIA API"}

@app.get("/estado_unifila")
def get_status():
    return {"estado": ESTADO}
