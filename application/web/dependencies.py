import fastapi

from ..core import postgres as _postgres


@fastapi.Depends
async def postgres():
    async with _postgres.session() as session:
        yield session
