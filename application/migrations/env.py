from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from application import models  # noqa: F401
from application.core import config
from application.core import postgres

metadata = postgres.metadata
alembic_config = context.config

fileConfig(alembic_config.config_file_name)


def run_migrations_online() -> None:
    database_url = config.postgres.url.replace(
        "postgresql",
        "postgresql+psycopg",
    )

    engine = create_engine(database_url)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata)

        with context.begin_transaction():
            context.run_migrations()


if not context.is_offline_mode():
    run_migrations_online()
