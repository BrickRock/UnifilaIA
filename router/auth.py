from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from database import db
from models import Paciente
import os
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "unifila-demo-secret-2024")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


class LoginRequest(BaseModel):
    user: str
    password: str


def _make_token(payload: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({**payload, "exp": int(expire.timestamp())}, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(body: LoginRequest, session: Session = Depends(get_db)):
    if body.user == "admin" and body.password == "admin":
        token = _make_token({"sub": "admin", "nss": "admin", "nombre": "Administrador", "role": "admin"})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"nss": "admin", "nombre": "Administrador", "role": "admin"},
        }

    paciente = session.execute(
        select(Paciente).where(Paciente.nss == body.user)
    ).scalar_one_or_none()

    if not paciente:
        raise HTTPException(status_code=401, detail="NSS no registrado. ¿Ya tienes cuenta?")

    token = _make_token({
        "sub": paciente.nss,
        "nss": paciente.nss,
        "nombre": paciente.nombre_completo,
        "id": paciente.id_paciente,
        "role": "patient",
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "nss": paciente.nss,
            "nombre": paciente.nombre_completo,
            "id": paciente.id_paciente,
            "role": "patient",
        },
    }
