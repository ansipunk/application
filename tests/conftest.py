import os

import alembic.command
import alembic.config
import pytest
import sqlalchemy
import sqlalchemy_utils

import application.core.config
import application.core.postgres
import application.models

from ._fixtures import *  # noqa: F403


@pytest.fixture(scope="session")
def worker_number(worker_id):
    try:
        return int(worker_id[2:]) + 1
    except ValueError:
        return 1


@pytest.fixture(scope="session", autouse=True)
def _test_context(worker_number):
    application.core.config.web.debug = True

    application.core.config.postgres.force_rollback = True
    application.core.config.postgres.database = (
        f"application-test-{worker_number}"
    )

    # Superuser permissions are required to install PostGIS extension.
    # Our test suite creates multiple new databases to be ran in parallel
    # and each of them needs the extension installed.
    #
    # It should not be of a security concern, as the application itself
    # does not require superuser permissions for the database.
    postgres_superuser_user = os.environ.get("ADMIN_POSTGRES_USER", "postgis")
    postgres_superuser_password = os.environ.get(
        "ADMIN_POSTGRES_PASSWORD",
        "postgis",
    )

    application.core.config.postgres.user = postgres_superuser_user
    application.core.config.postgres.password = postgres_superuser_password

    database_url = application.core.config.postgres.url.replace(
        "postgresql",
        "postgresql+psycopg",
    )

    if sqlalchemy_utils.database_exists(database_url):
        sqlalchemy_utils.drop_database(database_url)
    sqlalchemy_utils.create_database(database_url)

    engine = sqlalchemy.create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE EXTENSION pg_trgm;"))
        conn.execute(sqlalchemy.text("CREATE EXTENSION postgis;"))
        conn.commit()
    engine.dispose()

    alembic_config = alembic.config.Config("./alembic.ini")
    alembic.command.upgrade(alembic_config, "head")

    try:
        yield
    finally:
        sqlalchemy_utils.drop_database(database_url)


@pytest.fixture
async def postgres():
    await application.core.postgres.connect()

    try:
        async with application.core.postgres.session() as postgres:
            yield postgres
    finally:
        await application.core.postgres.disconnect()
