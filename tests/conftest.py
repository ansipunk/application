import alembic.command
import alembic.config
import pytest
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
    database_url = application.core.config.postgres.url.replace(
        "postgresql",
        "postgresql+psycopg",
    )

    if sqlalchemy_utils.database_exists(database_url):
        sqlalchemy_utils.drop_database(database_url)
    sqlalchemy_utils.create_database(database_url)

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
