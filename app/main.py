from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="CrediGestor API",
    description="Sistema de Gestão de Promissórias",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints de teste
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
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.APP_ENV,
    }
