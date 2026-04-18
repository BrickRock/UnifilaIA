from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# TODO: reemplazar con la cadena real cuando la BD esté levantada
# Formato PostgreSQL: "postgresql+psycopg2://user:password@host:port/dbname"
DATABASE_URL = "postgresql+psycopg2://user:password@10.45.179.6:5432/unifila"


class _Database:
    _instance: "_Database | None" = None

    def __new__(cls) -> "_Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._engine = create_engine(DATABASE_URL, echo=True)
            cls._instance._session_factory = sessionmaker(bind=cls._instance._engine)
        return cls._instance

    def get_session(self) -> Session:
        return self._session_factory()


# Punto de acceso global
db = _Database()
