"""
Application configuration.

Reads settings from environment variables (and a local .env file when present,
for running the API outside docker-compose). docker-compose injects the real
values for local dev — see infra/docker-compose.yml and the root .env.example.

Backend Architect: extend this with any additional settings your features need
(e.g. token TTLs per role, pagination defaults) rather than hardcoding values
in route modules.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Simhastha 2028 API"
    ENV: str = "development"

    # postgresql+psycopg2://<user>:<password>@<host>:<port>/<db>
    DATABASE_URL: str = (
        "postgresql+psycopg2://simhastha:simhastha_dev_password@localhost:5432/simhastha"
    )
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    JWT_ALGORITHM: str = "HS256"

    # Connection pool sizing for the API container.
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Pagination defaults/ceilings for every list endpoint.
    DEFAULT_PAGE_LIMIT: int = 50
    MAX_PAGE_LIMIT: int = 200

    # Credentials created by `python -m app.seed`. Development only: the seed
    # script refuses to run when ENV is not a development/test environment, so
    # these values cannot silently become production logins.
    SEED_SUPER_ADMIN_USERNAME: str = "admin"
    SEED_SUPER_ADMIN_PASSWORD: str = "Simhastha@2028"
    SEED_CONTENT_MANAGER_USERNAME: str = "content"
    SEED_CONTENT_MANAGER_PASSWORD: str = "Content@2028"

    # Comma-separated list of allowed origins for CORS.
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
