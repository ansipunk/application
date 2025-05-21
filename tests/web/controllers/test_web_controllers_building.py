import fastapi
import pytest

import application.models
import application.web.controllers
import application.web.schemas


async def test_create_building(mocker, postgres):
    address = "Address"
    longitude = 12.34
    latitude = 56.78

    building = application.web.schemas.BuildingCreate(
        address=address,
        longitude=longitude,
        latitude=latitude,
    )

    model_mock = mocker.spy(application.models, "building_create")

    created_building = await application.web.controllers.building_create(
        postgres,
        building,
    )

    assert created_building == model_mock.spy_return
    model_mock.assert_called_once_with(
        postgres,
        address=address,
        longitude=longitude,
        latitude=latitude,
    )


async def test_get_building(postgres, building_moscow_a):
    fetched_building = await application.web.controllers.building_get_by_id(
        postgres,
        building_moscow_a["id"],
    )
    assert fetched_building == building_moscow_a


async def test_get_nonexistent_building(postgres):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.building_get_by_id(postgres, 0)

    assert e.value.status_code == 404


async def test_get_buildings(postgres, building_moscow_a):
    buildings = await application.web.controllers.building_get(postgres)
    assert buildings == {"buildings": [building_moscow_a]}


async def test_get_buildings_within_radius(
    postgres,
    building_moscow_a,
    building_moscow_b,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 10  # 1o meters

    fetched_buildings = (
        await application.web.controllers.building_get_within_radius(
            postgres,
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius,
        )
    )

    assert fetched_buildings == {"buildings": [building_moscow_a]}


async def test_delete_building(mocker, postgres, building_moscow_a):
    model_mock = mocker.spy(application.models, "building_delete")
    await application.web.controllers.building_delete(
        postgres,
        building_moscow_a["id"],
    )
    model_mock.assert_called_once_with(postgres, building_moscow_a["id"])


async def test_delete_building_with_entities(
    postgres,
    building_moscow_a,
    organization_moscow_a_meat,
):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.building_delete(
            postgres,
            building_moscow_a["id"],
        )

    assert e.value.status_code == 400
