import fastapi

from .. import controllers
from .. import dependencies
from .. import responses
from .. import schemas

router = fastapi.APIRouter()


@router.post(
    "/",
    summary="Create a new organization",
    response_model=schemas.OrganizationGet,
    responses=responses.gen_responses(
        {
            400: (
                "Building or activity with provided ID does not exist "
                "or no activity IDs were provided"
            ),
        },
    ),
)
async def organization_create(
    organization: schemas.OrganizationCreate,
    session=dependencies.postgres,
):
    return await controllers.organization_create(session, organization)


@router.get(
    "/",
    summary="Get all organizations",
    response_model=schemas.OrganizationGetList,
)
async def organization_get(session=dependencies.postgres):
    return await controllers.organization_get(session)


@router.get(
    "/by_building",
    summary="Get organizations in a building with provided ID",
    response_model=schemas.OrganizationGetList,
)
async def organization_get_by_building_id(
    building_id: int,
    session=dependencies.postgres,
):
    return await controllers.organization_get_by_building_id(
        session,
        building_id,
    )


@router.get(
    "/by_activity",
    summary="Get organizations with an activity with provided ID",
    response_model=schemas.OrganizationGetList,
)
async def organization_get_by_activity_id(
    activity_id: int,
    include_nested: bool = False,
    session=dependencies.postgres,
):
    return await controllers.organization_get_by_activity_id(
        session,
        activity_id,
        include_nested=include_nested,
    )


@router.get(
    "/by_radius",
    summary="Get organizations within specified radius from a certain point",
    response_model=schemas.OrganizationGetList,
)
async def organization_get_by_radius(
    longitude: float,
    latitude: float,
    radius_meters: float,
    session=dependencies.postgres,
):
    return await controllers.organization_get_by_radius(
        session,
        longitude=longitude,
        latitude=latitude,
        radius=radius_meters,
    )


@router.get(
    "/search",
    summary="Find organizations by name",
    response_model=schemas.OrganizationGetList,
)
async def organization_search(query: str, session=dependencies.postgres):
    return await controllers.organization_search(session, query)


@router.get(
    "/{organization_id}",
    summary="Get an organization with provided ID",
    response_model=schemas.OrganizationGet,
    responses=responses.gen_responses(
        {
            404: "Organization does not exist",
        },
    ),
)
async def organization_get_by_id(
    organization_id: int,
    session=dependencies.postgres,
):
    return await controllers.organization_get_by_id(session, organization_id)


@router.delete(
    "/{organization_id}",
    summary="Delete an organization with provided ID",
)
async def organization_delete(
    organization_id: int,
    session=dependencies.postgres,
):
    return await controllers.organization_delete(session, organization_id)
