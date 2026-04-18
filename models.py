from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class TurnoSimplificado(Base):
    __tablename__ = "turno_simplificado"

    id = Column(Integer, primary_key=True)
    preventiva = Column(Integer, nullable=False)
    mas_de_un_sintoma = Column(Integer, nullable=False)
    adulto = Column(Integer, nullable=False)
    comorbilidad = Column(Integer, nullable=False)
    tiene_laboratorio = Column(Integer, nullable=False)
    es_seguimiento = Column(Integer, nullable=False)
    
    # El score se puede calcular al momento de insertar o guardar
    score = Column(Integer, nullable=False)
