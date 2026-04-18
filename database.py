import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base

_raw_url = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://Seguro13X:mysecretpassword@172.17.0.3:5432/imss",
)
# Railway provee "postgresql://..." pero psycopg2 necesita "postgresql+psycopg2://"
DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)


class _Database:
    _instance: "_Database | None" = None

    def __new__(cls) -> "_Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            engine = create_engine(DATABASE_URL, echo=False)
            # Retry hasta que Postgres esté listo (Railway puede tardar unos segundos)
            for attempt in range(10):
                try:
                    with engine.connect() as c:
                        c.execute(text("SELECT 1"))
                    break
                except Exception:
                    if attempt == 9:
                        raise
                    time.sleep(3)
            cls._instance._engine = engine
            Base.metadata.create_all(cls._instance._engine)
            with cls._instance._engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE turno_simplificado "
                    "ADD COLUMN IF NOT EXISTS duracion_estimada_minutos FLOAT"
                ))
                conn.execute(text(
                    "ALTER TABLE turno_simplificado "
                    "ADD COLUMN IF NOT EXISTS nss VARCHAR(11)"
                ))
                conn.commit()
            # Seed consultorios si la tabla está vacía
            with cls._instance._engine.connect() as conn2:
                count = conn2.execute(text("SELECT COUNT(*) FROM consultorio")).scalar() or 0
                if count == 0:
                    conn2.execute(text(
                        "INSERT INTO consultorio (numero, piso) VALUES "
                        "('101', 1), ('102', 1), ('201', 2)"
                    ))
                    conn2.commit()
            cls._instance._session_factory = sessionmaker(bind=cls._instance._engine)
        return cls._instance

    def get_session(self) -> Session:
        return self._session_factory()


# Punto de acceso global
db = _Database()
