from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base
# TODO: reemplazar con la cadena real cuando la BD esté levantada
# Formato PostgreSQL: "postgresql+psycopg2://user:password@host:port/dbname"
DATABASE_URL = "postgresql+psycopg2://Seguro13X:mysecretpassword@172.17.0.3:5432/imss"
#
#POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=Seguro13X
class _Database:
    _instance: "_Database | None" = None

    def __new__(cls) -> "_Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._engine = create_engine(DATABASE_URL, echo=True)
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
            cls._instance._session_factory = sessionmaker(bind=cls._instance._engine)
        return cls._instance

    def get_session(self) -> Session:
        return self._session_factory()


# Punto de acceso global
db = _Database()
