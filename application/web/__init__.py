from contextlib import asynccontextmanager

import fastapi
import fastapi.responses

from ..core import config
from ..core import postgres
from . import api


@asynccontextmanager
async def lifespan(_):
    await postgres.connect()

    try:
        yield
    finally:
        await postgres.disconnect()


app = fastapi.FastAPI(
    title="Application",
    summary=f"Current API Key: {config.web.api_key}",
    version="0.1.0",
    redirect_slashes=False,
    redoc_url=None,
    debug=config.web.debug,
    lifespan=lifespan,
    default_response_class=fastapi.responses.ORJSONResponse,
)

app.include_router(api.router, prefix="/api")


@app.get(
    "/",
    summary="Redirect to OpenAPI docs",
    status_code=fastapi.status.HTTP_307_TEMPORARY_REDIRECT,
    response_model=None,
)
def redirect_to_docs():
    return fastapi.responses.RedirectResponse("/docs")
