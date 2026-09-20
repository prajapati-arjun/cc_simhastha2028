"""
Alembic environment script.

DevOps-owned scaffold: wires alembic to read DATABASE_URL from app settings
(env var, same value docker-compose injects into the api container) so
`alembic revision` / `alembic upgrade head` work mechanically as soon as
Backend Architect adds models.

Backend Architect: once app/db/base.py (SQLAlchemy declarative Base) and
app/models/* exist, import your models' metadata below and set
`target_metadata = Base.metadata` so `alembic revision --autogenerate` works.
Until then this scaffold supports hand-written revisions.
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make the `app` package importable when alembic is invoked from apps/api/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings  # noqa: E402

# this is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from application settings (env var DATABASE_URL)
# rather than hardcoding it in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# TODO (Backend Architect): replace with `from app.db.base import Base` and
# `target_metadata = Base.metadata` once models exist, to enable autogenerate.
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emits SQL, no live DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
