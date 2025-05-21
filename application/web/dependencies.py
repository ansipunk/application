import fastapi
import fastapi.security

from ..core import config
from ..core import postgres as _postgres

api_key_header = fastapi.security.APIKeyHeader(name="X-Application-API-Key")


@fastapi.Depends
async def postgres():
    async with _postgres.session() as session:
        yield session


@fastapi.Depends
async def auth(api_key=fastapi.Depends(api_key_header)):
    if api_key != config.web.api_key:
        raise fastapi.HTTPException(403, "Not authenticated")
