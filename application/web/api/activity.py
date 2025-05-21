import fastapi

from .. import controllers
from .. import dependencies
from .. import responses
from .. import schemas

router = fastapi.APIRouter()


@router.post(
    "/",
    summary="Create a new activity",
    response_model=schemas.ActivityGet,
    responses=responses.gen_responses(
        {
            400: (
                "Parent activity does not exist "
                "or activity nesting limit reached"
            ),
        },
    ),
)
async def activity_create(
    activity: schemas.ActivityCreate,
    session=dependencies.postgres,
):
    return await controllers.activity_create(session, activity)


@router.get(
    "/",
    summary="Get all activities",
    response_model=schemas.ActivityGetList,
)
async def activity_get(session=dependencies.postgres):
    return await controllers.activity_get(session)


@router.get(
    "/{activity_id}",
    summary="Get an activity by its ID",
    responses=responses.gen_responses(
        {
            404: "Activity does not exist",
        },
    ),
)
async def activity_get_by_id(activity_id: int, session=dependencies.postgres):
    return await controllers.activity_get_by_id(session, activity_id)


@router.delete(
    "/{activity_id}",
    summary="Delete an activity by its ID",
)
async def activity_delete(activity_id: int, session=dependencies.postgres):
    return await controllers.activity_delete(session, activity_id)
