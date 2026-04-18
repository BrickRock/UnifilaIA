from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    user: str
    password: str

@router.post("/login")
def login(body: LoginRequest):
    # Lógica de validación de credenciales
    if body.user == "admin" and body.password == "admin":
        return {"message": "Login exitoso"}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")
