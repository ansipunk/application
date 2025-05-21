import fastapi

from .activity import router as activity_router
from .building import router as building_router

router = fastapi.APIRouter()

router.include_router(building_router, prefix="/buildings")
router.include_router(activity_router, prefix="/activities")
