from pathlib import Path
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import create_engine, Session

# Ruta absoluta al archivo database.db basada en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
db_path = BASE_DIR / "database.db"
sqlite_url = f"sqlite:///{db_path.as_posix()}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


# Activa el soporte de claves foráneas en SQLite para consistencia referencial
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_session():
    with Session(engine) as session:
        yield session
