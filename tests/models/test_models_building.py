import pytest

import application.models


async def test_create_and_get_building(postgres):
    address = "ул. Пушкина, д. Колотушкина"
    longitude = 12.34
    latitude = 56.78

    created_building = await application.models.building_create(
        postgres,
        address=address,
        longitude=longitude,
        latitude=latitude,
    )

    assert created_building is not None
    assert created_building["id"] is not None
    assert created_building["address"] == address
    assert created_building["longitude"] == longitude
    assert created_building["latitude"] == latitude


async def test_get_building(postgres, building_moscow_a):
    fetched_building = await application.models.building_get_by_id(
        postgres,
        building_moscow_a["id"],
    )

    assert fetched_building["id"] == building_moscow_a["id"]
    assert fetched_building["address"] == building_moscow_a["address"]
    assert fetched_building["longitude"] == building_moscow_a["longitude"]
    assert fetched_building["latitude"] == building_moscow_a["latitude"]


async def test_get_nonexistent_building(postgres):
    with pytest.raises(application.models.BuildingDoesNotExist):
        await application.models.building_get_by_id(postgres, 0)


async def test_get_buildings(
    postgres,
    building_moscow_a,
    building_moscow_b,
    building_minsk_a,
    building_minsk_b,
):
    buildings = await application.models.building_get(postgres)
    assert len(buildings) == 4

    for building in (
        building_moscow_a,
        building_moscow_b,
        building_minsk_a,
        building_minsk_b,
    ):
        assert building in buildings


async def test_get_buildings_within_radius_tiny(
    postgres,
    building_moscow_a,
    building_moscow_b,
    building_minsk_a,
    building_minsk_b,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 100  # 100 meters

    buildings = await application.models.building_get_within_radius(
        postgres,
        origin_longitude=longitude,
        origin_latitude=latitude,
        radius_meters=radius,
    )

    assert len(buildings) == 1
    assert buildings == [building_moscow_a]


async def test_get_buildings_within_radius_medium(
    postgres,
    building_moscow_a,
    building_moscow_b,
    building_minsk_a,
    building_minsk_b,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 25 * 1000  # 25 kilometers

    buildings = await application.models.building_get_within_radius(
        postgres,
        origin_longitude=longitude,
        origin_latitude=latitude,
        radius_meters=radius,
    )

    assert len(buildings) == 2
    assert buildings == [building_moscow_a, building_moscow_b]


async def test_get_buildings_within_radius_large(
    postgres,
    building_moscow_a,
    building_moscow_b,
    building_minsk_a,
    building_minsk_b,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 5000 * 1000  # 5000 kilometers

    buildings = await application.models.building_get_within_radius(
        postgres,
        origin_longitude=longitude,
        origin_latitude=latitude,
        radius_meters=radius,
    )

    assert len(buildings) == 4

    for building in (
        building_moscow_a,
        building_moscow_b,
        building_minsk_a,
        building_minsk_b,
    ):
        assert building in buildings


async def test_get_buildings_within_radius_no_results(
    postgres,
    building_moscow_a,
    building_moscow_b,
    building_minsk_a,
    building_minsk_b,
):
    longitude = 0
    latitude = 0
    radius = 50 * 1000  # 50 kilometers

    buildings = await application.models.building_get_within_radius(
        postgres,
        origin_longitude=longitude,
        origin_latitude=latitude,
        radius_meters=radius,
    )

    assert len(buildings) == 0


async def test_delete_building(postgres, building_moscow_a):
    await application.models.building_delete(postgres, building_moscow_a["id"])

    with pytest.raises(application.models.BuildingDoesNotExist):
        await application.models.building_get_by_id(
            postgres,
            building_moscow_a["id"],
        )


async def test_delete_building_with_organizations(
    postgres,
    building_moscow_a,
    organization_moscow_a_meat,
):
    with pytest.raises(application.models.BuildingHasEntities):
        await application.models.building_delete(
            postgres,
            building_moscow_a["id"],
        )
