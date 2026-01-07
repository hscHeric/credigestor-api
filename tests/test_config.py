from app.config import Settings


def test_settings_database_urls_and_env_flags():
    s = Settings(
        APP_ENV="production",
        DB_HOST="h",
        DB_PORT=1234,
        DB_USER="u",
        DB_PASSWORD="p",
        DB_NAME="db",
    )

    assert s.DATABASE_URL == "postgresql://u:p@h:1234/db"
    assert s.DATABASE_URL_ASYNC == "postgresql+asyncpg://u:p@h:1234/db"
    assert s.is_development is False
    assert s.is_production is True
