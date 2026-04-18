from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils import ESTADOS_UNIFILA
from models import RegistrarPacienteRequest, PacienteFormado, EstadoAtencion, RegistroPresencialRequest
from database import db
from services import QueueService
from models import Paciente, PacienteFormado
from schemas import PacienteCreate, PacienteFormadoCreate
from database import db
from router import atencion, pacientes, auth

app = FastAPI(title="UnifilaIA API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["*"],  # En producción deberías especificar los orígenes permitidos
=======
    allow_origins=["http://localhost:5173"],
>>>>>>> 072870bb2affacbeb2ec463533400f06e6009fed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los nuevos routers
app.include_router(atencion.router)
app.include_router(pacientes.router)
app.include_router(auth.router)

ESTADO = ESTADOS_UNIFILA.NORMAL.value

@app.get("/health")
def health_check():
    try:
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB no disponible: {e}")

ESTADO = ESTADOS_UNIFILA.NORMAL.value

@app.get("/")
def read_root():
    return {"message": "Bienvenido a UnifilaIA API"}

@app.get("/estado_unifila")
def get_status():
    return {"estado": ESTADO}


@app.post("/pacientes", status_code=201)
def registrar_paciente(body: PacienteCreate):
    if ESTADO == ESTADOS_UNIFILA.SATURADO.value:
        raise HTTPException(status_code=400, detail="Sistema saturado no se aceptan nuevos pacientes en unifila")
    session = db.get_session()
    try:
        paciente = Paciente(**body.model_dump())
        session.add(paciente)
        session.commit()
        session.refresh(paciente)
        return {"mensaje": "Paciente registrado", "id_paciente": paciente.id_paciente, "status" : ESTADO}
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un paciente con ese NSS ({body.nss})."
        )
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar paciente: {e}")
    finally:
        session.close()

    paciente = {
        "id": len(pacientes_db) + 1,
        "nombre": body.nombre,
        "apellido": body.apellido,
        "curp": body.curp,
        "estado": EstadoAtencion.EN_ESPERA.value
    }
    pacientes_db.append(paciente)

    # TODO: persistir con db.get_session() cuando la BD esté levantada
    return {"mensaje": "Paciente registrado", "paciente": paciente}


@app.post("/pacientes/{id_turno}/cancelar", status_code=200)
def cancelar_paciente(id_turno: int):
    """
    Cancela un registro en la cola de atención por su ID.
    """
    for p in pacientes_db:
        if p["id"] == id_turno:
            p["estado"] = EstadoAtencion.CANCELADO.value
            break
            
    exito = QueueService.cancelar_turno(id_turno)
    if not exito:
        return {"mensaje": f"Turno {id_turno} cancelado en memoria"}
    
    return {"mensaje": f"Turno {id_turno} cancelado con éxito"}


@app.post("/mantenimiento/limpiar-espera-excesiva", status_code=200)
def limpiar_espera_excesiva(minutos: int = 60):
    """
    Busca y cancela automáticamente todos los turnos que excedan el tiempo de espera.
    """
    cancelados = QueueService.cancelar_por_tiempo_espera(minutos)
    return {
        "mensaje": "Limpieza de cola completada", 
        "total_cancelados": cancelados,
        "criterio_minutos_maximo": minutos
    }


@app.get("/pacientes/{id_turno}/estado", status_code=200)
def consultar_estado_lugar(id_turno: int):
    """
    Consulta la posición actual, personas por delante y tiempo estimado de espera.
    """
    resultado = QueueService.obtener_posicion_cola(id_turno)
    
    if resultado is None:
        # Respaldo para lista mock
        for p in pacientes_db:
            if p["id"] == id_turno:
                return {
                    "id": id_turno,
                    "nombre": p["nombre"],
                    "estado": p.get("estado", "En_Espera"),
                    "mensaje": "Datos desde memoria temporal"
                }
        raise HTTPException(status_code=404, detail="Turno no encontrado")
        
    return resultado


@app.post("/pacientes/presencial", status_code=201)
def registrar_presencial(body: RegistroPresencialRequest):
    """
    Registra a un paciente de manera presencial en la clínica.
    """
    try:
        nuevo_turno = QueueService.registrar_presencial(body)
        return {
            "mensaje": "Paciente registrado presencialmente",
            "id_turno": nuevo_turno.id_turno_dia,
            "paciente": body.nombre_completo,
            "consultorio": body.id_consultorio,
            "estado": nuevo_turno.estado_atencion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en registro presencial: {e}")

@app.post("/pacientes-formados", status_code=201)
def registrar_paciente_formado(body: PacienteFormadoCreate):
    session = db.get_session()
    try:
        formado = PacienteFormado(**body.model_dump())
        session.add(formado)
        session.commit()
        session.refresh(formado)
        return {"mensaje": "Paciente formado registrado", "id_turno_dia": formado.id_turno_dia}
    except IntegrityError as e:
        session.rollback()
        orig = str(e.orig)
        if "id_paciente" in orig:
            detail = f"No existe un paciente con id {body.id_paciente}."
        elif "id_consultorio" in orig:
            detail = f"No existe un consultorio con id {body.id_consultorio}."
        else:
            detail = "Violación de integridad en la BD."
        raise HTTPException(status_code=409, detail=detail)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar paciente formado: {e}")
    finally:
        session.close()
