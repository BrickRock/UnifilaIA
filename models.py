from pydantic import BaseModel


class RegistrarPacienteRequest(BaseModel):
    nombre: str
    apellido: str
    curp: str