from contextlib import asynccontextmanager

from based import Database
from sqlalchemy import MetaData

from . import config


class PostgresNotConnectedError(Exception):
    pass


_pool = None
metadata = MetaData()


async def connect():
    global _pool  # noqa: PLW0603

    if _pool is None:
        _pool = Database(
            config.postgres.url,
            force_rollback=config.postgres.force_rollback,
        )

        await _pool.connect()


async def disconnect():
    global _pool  # noqa: PLW0603

    if _pool is not None:
        await _pool.disconnect()
        _pool = None


@asynccontextmanager
async def session():
    if _pool is None:
        raise PostgresNotConnectedError

    async with _pool.session() as session:
        yield session
