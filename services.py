from datetime import datetime, timedelta, date
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models import PacienteFormado, EstadoAtencion, Paciente, RegistroPresencialRequest
from database import db

class QueueService:
    @staticmethod
    def registrar_presencial(data: RegistroPresencialRequest) -> PacienteFormado:
        """
        Registra a un paciente físicamente en la clínica.
        1. Busca si el paciente ya existe (por NSS).
        2. Si no, lo crea.
        3. Le genera un turno activo (PacienteFormado).
        """
        with db.get_session() as session:
            # 1. Buscar o crear Paciente
            paciente = session.query(Paciente).filter(Paciente.nss == data.nss).first()
            if not paciente:
                paciente = Paciente(
                    nss=data.nss,
                    nombre_completo=data.nombre_completo,
                    fecha_nacimiento=date.fromisoformat(data.fecha_nacimiento),
                    sexo=data.sexo,
                    es_cronico_general=data.es_cronico
                )
                session.add(paciente)
                session.flush() # Para obtener el ID generado

            # 2. Calcular edad (aproximada para fines médicos)
            f_nac = date.fromisoformat(data.fecha_nacimiento)
            edad = date.today().year - f_nac.year

            # 3. Crear Turno
            nuevo_turno = PacienteFormado(
                id_paciente=paciente.id_paciente,
                id_consultorio=data.id_consultorio,
                telefono=data.telefono,
                tipo_consulta=data.tipo_consulta,
                indicador_cronicidad=data.es_cronico,
                edad_al_momento=edad,
                estado_atencion=EstadoAtencion.EN_ESPERA,
                hora_llegada=datetime.now()
            )
            session.add(nuevo_turno)
            session.commit()
            session.refresh(nuevo_turno)
            return nuevo_turno
    @staticmethod
    def cancelar_por_tiempo_espera(minutos_maximo: int = 60) -> int:
        """
        Busca y cancela todos los turnos en espera que lleven más de 
        'minutos_maximo' sin ser atendidos.
        """
        ahora = datetime.now()
        limite = ahora - timedelta(minutes=minutos_maximo)
        
        with db.get_session() as session:
            # Buscar turnos que excedan el tiempo y sigan en espera
            query = select(PacienteFormado).where(
                PacienteFormado.estado_atencion == EstadoAtencion.EN_ESPERA,
                PacienteFormado.hora_llegada < limite
            )
            
            turnos_a_cancelar = session.scalars(query).all()
            total_cancelados = len(turnos_a_cancelar)
            
            for turno in turnos_a_cancelar:
                turno.estado_atencion = EstadoAtencion.CANCELADO
            
            session.commit()
            return total_cancelados

    @staticmethod
    def cancelar_turno(id_turno: int) -> bool:
        """Cancela un turno específico por su ID."""
        with db.get_session() as session:
            turno = session.get(PacienteFormado, id_turno)
            if turno:
                turno.estado_atencion = EstadoAtencion.CANCELADO
                session.commit()
                return True
            return False

    @staticmethod
    def obtener_posicion_cola(id_turno: int) -> dict:
        """
        Calcula la posición del paciente en la cola y estadísticas de espera.
        """
        with db.get_session() as session:
            turno_actual = session.get(PacienteFormado, id_turno)
            if not turno_actual:
                return None
            
            if turno_actual.estado_atencion != EstadoAtencion.EN_ESPERA:
                return {
                    "estado": turno_actual.estado_atencion,
                    "lugar": 0,
                    "personas_adelante": 0,
                    "tiempo_estimado_min": 0
                }

            # Contar cuántos pacientes llegaron ANTES al mismo consultorio y siguen en espera
            query = select(func.count(PacienteFormado.id_turno_dia)).where(
                PacienteFormado.id_consultorio == turno_actual.id_consultorio,
                PacienteFormado.estado_atencion == EstadoAtencion.EN_ESPERA,
                PacienteFormado.hora_llegada < turno_actual.hora_llegada
            )
            
            personas_adelante = session.execute(query).scalar()
            lugar = personas_adelante + 1
            
            # Estimación simple: 10 minutos por persona por delante
            tiempo_estimado = personas_adelante * 10 
            
            return {
                "estado": turno_actual.estado_atencion,
                "lugar": lugar,
                "personas_adelante": personas_adelante,
                "tiempo_estimado_min": tiempo_estimado,
                "consultorio": turno_actual.id_consultorio
            }
