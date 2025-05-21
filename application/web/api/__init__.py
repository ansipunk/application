import fastapi

from .activity import router as activity_router
from .building import router as building_router
from .organization import router as organization_router

router = fastapi.APIRouter()

router.include_router(
    building_router,
    prefix="/buildings",
    tags=["buildings"],
)

router.include_router(
    activity_router,
    prefix="/activities",
    tags=["activities"],
)

router.include_router(
    organization_router,
    prefix="/organizations",
    tags=["organizations"],
)
