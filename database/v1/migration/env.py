from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from model.v1 import (
    audit_log,
    module_model,
    user_model,
    role_model,
    permission_model,
    user_session_model,
)

import os
from config.v1.config_dev import Base, Config  # import your Base & Config class

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set metadata
target_metadata = Base.metadata

# Override the URL from our config
config.set_main_option("sqlalchemy.url", Config.DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
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
