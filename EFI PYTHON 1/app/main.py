import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Garantizar que el directorio raíz del proyecto esté en sys.path para permitir ejecución directa
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from pathlib import Path
from alembic import command
BASE_DIR = Path(__file__).resolve().parent.parent


def run_migrations():
    ini_path = BASE_DIR / "alembic.ini"
    alembic_dir = BASE_DIR / "alembic"

    # Verificación rápida en los logs para confirmar que se subieron los archivos
    if not ini_path.exists():
        raise FileNotFoundError(f"No se encontró alembic.ini en: {ini_path}")

    alembic_cfg = Config(str(ini_path))

    # Forzamos la ruta absoluta de la carpeta de migraciones
    alembic_cfg.set_main_option("script_location", str(alembic_dir))

    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield

app = FastAPI(lifespan=lifespan)    

from app.db import engine
# Importación de los routers del proyecto
from app.routers import edificio, elevador, mantenimiento


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de tablas en caso de ejecución directa sin migraciones previas
    SQLModel.metadata.create_all(engine)
    yield


# 1. Instanciación de FastAPI con metadatos personalizados y lifespan
app = FastAPI(
    title="Elevadores Norte - API de Gestión de Elevadores y Mantenimientos",
    description=(
        "Sistema RESTful modularizado de Elevadores Norte para el control y seguimiento de edificios, "
        "elevadores instalados y mantenimientos técnicos programados."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# 2. Configuración de CORS
# Permite la conexión desde el cliente web (frontend de la EFI de React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Registro de Routers
app.include_router(edificio.router)
app.include_router(elevador.router)
app.include_router(mantenimiento.router)


# 4. Configuración global de la paginación
add_pagination(app)


# Endpoint de verificación de estado
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "API de Elevadores y Mantenimientos activa",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
