from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Configurações Gerais
    PORT: int = 8000
    APP_ENV: str = "development"

    # Banco de Dados
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "credigestor"
    DB_PASSWORD: str = "credigestor"
    DB_NAME: str = "credigestor_db"
    DB_SSLMODE: str = "require"  # Padrão 'require' para funcionar com Neon

    # Segurança
    JWT_SECRET: str = "credigestor"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # E-mail (Opcional)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@credigestor.com"
    SMTP_FROM_NAME: str = "CrediGestor"

    # URLs
    FRONTEND_URL: str = "http://localhost:3000"

    # Configuração do Pydantic para ler o .env e variáveis de ambiente
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    @property
    def DATABASE_URL(self) -> str:
        """Constrói a URL do banco de dados com suporte a SSL (necessário para Neon/Vercel)"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """URL para uso com asyncpg se necessário"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


# Instância única de configurações usada em todo o projeto
settings = Settings()
