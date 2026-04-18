from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import db
from utils import ESTADOS_UNIFILA
from router import atencion, pacientes, auth, turnos, consultorios, consultas

app = FastAPI(title="UnifilaIA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(atencion.router)
app.include_router(pacientes.router)
app.include_router(auth.router)
app.include_router(turnos.router)
app.include_router(consultorios.router)
app.include_router(consultas.router)

ESTADO = ESTADOS_UNIFILA.NORMAL.value


@app.get("/health")
def health_check():
    try:
        session = db.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        return {"db": "ok"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail=f"DB no disponible: {e}")


@app.get("/")
def read_root():
    return {"message": "Bienvenido a UnifilaIA API"}


@app.get("/estado_unifila")
def get_status():
    return {"estado": ESTADO}
