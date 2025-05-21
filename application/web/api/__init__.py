import fastapi

from .building import router as building_router

router = fastapi.APIRouter()

router.include_router(building_router, prefix="/buildings")
