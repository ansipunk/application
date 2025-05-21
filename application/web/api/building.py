import fastapi

from .. import controllers
from .. import dependencies
from .. import responses
from .. import schemas

router = fastapi.APIRouter()


@router.post(
    "/",
    summary="Create a new building",
    response_model=schemas.BuildingGet,
)
async def building_create(
    building: schemas.BuildingCreate,
    session=dependencies.postgres,
):
    return await controllers.building_create(session, building)


@router.get(
    "/",
    summary="Get all buildings",
    response_model=schemas.BuildingGetList,
)
async def building_get(session=dependencies.postgres):
    return await controllers.building_get(session)


@router.get(
    "/by_radius",
    summary="Get buildings within given radius from a certain point",
    response_model=schemas.BuildingGetList,
)
async def building_get_by_radius(
    longitude: float,
    latitude: float,
    radius_meters: float,
    session=dependencies.postgres,
):
    return await controllers.building_get_within_radius(
        session=session,
        longitude=longitude,
        latitude=latitude,
        radius_meters=radius_meters,
    )


@router.get(
    "/{building_id}",
    summary="Get a building by its ID",
    response_model=schemas.BuildingGet,
    responses=responses.gen_responses(
        {
            404: "Building does not exist",
        },
    ),
)
async def building_get_by_id(building_id: int, session=dependencies.postgres):
    return await controllers.building_get_by_id(session, building_id)


@router.delete(
    "/{building_id}",
    summary="Delete a building",
    responses=responses.gen_responses(
        {
            400: "Building has entities attached to it",
        },
    ),
)
async def building_delete(building_id: int, session=dependencies.postgres):
    await controllers.building_delete(session, building_id)
