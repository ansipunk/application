import based
import fastapi

from ... import models
from .. import schemas


async def organization_create(
    session: based.Session,
    organization: schemas.OrganizationCreate,
):
    try:
        return await models.organization_create(
            session,
            name=organization.name,
            building_id=organization.building_id,
            activity_ids=organization.activity_ids,
        )
    except models.OrganizationActivitiesNotProvided:
        raise fastapi.HTTPException(
            400,
            "Organization activity IDs were not provided",
        )
    except models.BuildingDoesNotExist:
        raise fastapi.HTTPException(400, "Building does not exist")
    except models.ActivityDoesNotExist:
        raise fastapi.HTTPException(400, "Activity does not exist")


async def organization_get_by_id(session: based.Session, organization_id: int):
    try:
        return await models.organization_get_by_id(session, organization_id)
    except models.OrganizationDoesNotExist:
        raise fastapi.HTTPException(404, "Organization does not exist")


async def organization_get(session: based.Session):
    return {"organizations": await models.organization_get(session)}


async def organization_get_by_building_id(
    session: based.Session,
    building_id: int,
):
    return {
        "organizations": await models.organization_get_by_building_id(
            session,
            building_id,
        ),
    }


async def organization_get_by_activity_id(
    session: based.Session,
    activity_id: int,
    *,
    include_nested: bool = False,
):
    if include_nested:
        return {
            "organizations": await models.organization_get_by_nested_activities(
                session,
                activity_id,
            ),
        }

    return {
        "organizations": await models.organization_get_by_activity_id(
            session,
            activity_id,
        ),
    }


async def organization_get_by_radius(
    session: based.Session,
    *,
    longitude: float,
    latitude: float,
    radius: float,
):
    return {
        "organizations": await models.organization_get_within_radius(
            session,
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius,
        ),
    }


async def organization_search(session: based.Session, query: str):
    return {"organizations": await models.organization_search(session, query)}


async def organization_delete(session: based.Session, organization_id: int):
    await models.organization_delete(session, organization_id)
