import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.config import settings
    from app.database import engine, Base
    from app.models import User, Customer, Sale, PromissoryNote, Payment, SystemConfig  # noqa: F401
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação:
    Executa o que está antes do yield no startup e o que está depois no shutdown.
    """
    try:
        logger.info("Tentando conectar ao banco de dados e criar tabelas...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas/verificadas com sucesso!")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tabelas no banco: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        logger.warning(
            "A aplicação continuará rodando, mas operações de banco podem falhar."
        )
        logger.warning("Certifique-se de que o PostgreSQL está rodando: mise run up")

    yield  # Aplicação recebe as requisições aqui

    logger.info("Desligando aplicação...")


app = FastAPI(
    title="CrediGestor API",
    description="Sistema de Gestão de Promissórias",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "CrediGestor API",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "docs": "/docs" if settings.is_development else "disabled",
    }


@app.get("/health")
def health_check():
    """Endpoint de health check para monitoramento"""
    database_status = "unknown"
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception as e:
        database_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy" if database_status == "connected" else "degraded",
        "database": database_status,
        "environment": settings.APP_ENV,
    }
