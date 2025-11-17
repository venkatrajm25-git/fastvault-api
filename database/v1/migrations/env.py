from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from model.v1 import (
    audit_log,
    user_model,
    module_model,
    permission_model,
    role_model,
    user_session_model,
)

# Import your SQLAlchemy Base metadata (adjust this path)
from model.v1.base_env import Base

target_metadata = Base.metadata

# Get DATABASE_URL dynamically from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL not found in .env file")

# Override the URL inside alembic.ini dynamically
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
