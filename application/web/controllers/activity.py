import based
import fastapi

from ... import models
from .. import schemas


async def activity_create(
    session: based.Session,
    activity: schemas.ActivityCreate,
):
    try:
        return await models.activity_create(
            session,
            name=activity.name,
            parent_id=activity.parent_id,
        )
    except models.ActivityNestingLimitReached:
        raise fastapi.HTTPException(400, "Activity nesting limit reached")


async def activity_get_by_id(session: based.Session, activity_id: int):
    try:
        return await models.activity_get_by_id(session, activity_id)
    except models.ActivityDoesNotExist:
        raise fastapi.HTTPException(404, "Activity does not exist")


async def activity_get(session: based.Session):
    return {"activities": await models.activity_get(session)}


async def activity_delete(session: based.Session, activity_id: int):
    try:
        await models.activity_delete(session, activity_id)
    except models.ActivityHasEntities:
        raise fastapi.HTTPException(400, "Activity has entities attached to it")
