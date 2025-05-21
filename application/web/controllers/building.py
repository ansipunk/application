import based
import fastapi

from ... import models
from .. import schemas


async def building_create(
    session: based.Session,
    building: schemas.BuildingCreate,
):
    return await models.building_create(
        session,
        address=building.address,
        longitude=building.longitude,
        latitude=building.latitude,
    )


async def building_get_by_id(session: based.Session, building_id: int):
    try:
        return await models.building_get_by_id(session, building_id)
    except models.BuildingDoesNotExist:
        raise fastapi.HTTPException(404, "Requested building does not exist")


async def building_get(session: based.Session):
    return {
        "buildings": await models.building_get(session),
    }


async def building_get_within_radius(
    session: based.Session,
    *,
    longitude: float,
    latitude: float,
    radius_meters: float,
):
    return {
        "buildings": await models.building_get_within_radius(
            session,
            origin_longitude=longitude,
            origin_latitude=latitude,
            radius_meters=radius_meters,
        ),
    }


async def building_delete(session: based.Session, building_id: int):
    try:
        await models.building_delete(session, building_id)
    except models.BuildingHasEntities:
        raise fastapi.HTTPException(400, "Building has entities attached to it")
