import fastapi
import pytest

import application.models
import application.web.controllers
import application.web.schemas


async def test_create_organization(
    mocker,
    postgres,
    building_moscow_a,
    activity_food,
):
    name = "Name"
    building_id = building_moscow_a["id"]
    activity_ids = [activity_food["id"]]
    phone_numbers = ["+7 999 666 9999"]

    organization = application.web.schemas.OrganizationCreate(
        name=name,
        building_id=building_id,
        activity_ids=activity_ids,
        phone_numbers=phone_numbers,
    )

    model_mock = mocker.spy(application.models, "organization_create")

    created_organization = (
        await application.web.controllers.organization_create(
            postgres,
            organization,
        )
    )

    assert created_organization == model_mock.spy_return
    model_mock.assert_called_once_with(
        postgres,
        name=name,
        building_id=building_id,
        activity_ids=activity_ids,
        phone_numbers=phone_numbers,
    )


async def test_create_organization_without_activity_ids(
    postgres,
    building_moscow_a,
):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.organization_create(
            postgres,
            application.web.schemas.OrganizationCreate(
                name="Name",
                building_id=building_moscow_a["id"],
                activity_ids=[],
                phone_numbers=["+7 999 666 9999"],
            ),
        )

    assert e.value.status_code == 400


async def test_create_organization_with_nonexistent_building(
    postgres,
    activity_food,
):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.organization_create(
            postgres,
            application.web.schemas.OrganizationCreate(
                name="Name",
                building_id=0,
                activity_ids=[activity_food["id"]],
                phone_numbers=["+7 999 666 9999"],
            ),
        )

    assert e.value.status_code == 400


async def test_create_organization_with_nonexistent_activity(
    postgres,
    building_moscow_a,
):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.organization_create(
            postgres,
            application.web.schemas.OrganizationCreate(
                name="Name",
                building_id=building_moscow_a["id"],
                activity_ids=[0],
                phone_numbers=["+7 999 666 9999"],
            ),
        )

    assert e.value.status_code == 400


async def test_get_organization(postgres, organization_moscow_a_meat):
    fetched_organization = (
        await application.web.controllers.organization_get_by_id(
            postgres,
            organization_moscow_a_meat["id"],
        )
    )
    assert fetched_organization == organization_moscow_a_meat


async def test_get_nonexistent_organization(postgres):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.organization_get_by_id(postgres, 0)

    assert e.value.status_code == 404


async def test_get_organizations(
    mocker,
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
):
    model_mock = mocker.spy(application.models, "organization_get")
    fetched_organizations = await application.web.controllers.organization_get(
        postgres,
    )
    assert fetched_organizations == {"organizations": model_mock.spy_return}


async def test_get_organizations_by_building_id(
    postgres,
    organization_moscow_a_meat,
    building_moscow_a,
):
    fetched_organizations = (
        await application.web.controllers.organization_get_by_building_id(
            postgres,
            building_id=building_moscow_a["id"],
        )
    )
    assert fetched_organizations == {
        "organizations": [organization_moscow_a_meat],
    }


async def test_get_organizations_by_activity_id(
    postgres,
    organization_moscow_a_meat,
    activity_meat,
):
    fetched_organizations = (
        await application.web.controllers.organization_get_by_activity_id(
            postgres,
            activity_id=activity_meat["id"],
        )
    )
    assert fetched_organizations == {
        "organizations": [organization_moscow_a_meat],
    }


async def test_get_organizations_by_activity_id_nested(
    mocker,
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    activity_food,
):
    model_mock = mocker.spy(
        application.models,
        "organization_get_by_nested_activities",
    )
    fetched_organizations = (
        await application.web.controllers.organization_get_by_activity_id(
            postgres,
            activity_id=activity_food["id"],
            include_nested=True,
        )
    )
    model_mock.assert_called_once_with(postgres, activity_food["id"])
    assert fetched_organizations == {"organizations": model_mock.spy_return}


async def test_get_organizations_by_radius(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    building_moscow_a,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 25 * 1000  # 25 kilometers

    fetched_organizations = (
        await application.web.controllers.organization_get_by_radius(
            postgres,
            longitude=longitude,
            latitude=latitude,
            radius=radius,
        )
    )
    assert fetched_organizations == {
        "organizations": [
            organization_moscow_a_meat,
            organization_moscow_b_sausages_parts,
        ],
    }


async def test_organization_search(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    organization_minsk_b_buses,
):
    fetched_organizations = (
        await application.web.controllers.organization_search(postgres, "авто")
    )
    assert fetched_organizations == {
        "organizations": [
            organization_minsk_b_buses,
            organization_minsk_a_passenger_cars,
        ],
    }


async def test_organization_delete(
    mocker,
    postgres,
    organization_moscow_a_meat,
):
    model_mock = mocker.spy(application.models, "organization_delete")
    await application.web.controllers.organization_delete(
        postgres,
        organization_moscow_a_meat["id"],
    )
    model_mock.assert_called_once_with(
        postgres,
        organization_moscow_a_meat["id"],
    )
