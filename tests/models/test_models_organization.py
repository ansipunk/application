import pytest

import application.models


async def test_create_organization(postgres, building_moscow_a, activity_food):
    name = "Organization"
    building_id = building_moscow_a["id"]
    activity_ids = [activity_food["id"]]

    created_organization = await application.models.organization_create(
        postgres,
        name=name,
        building_id=building_id,
        activity_ids=activity_ids,
    )

    assert created_organization is not None
    assert created_organization["id"] is not None
    assert created_organization["name"] == name
    assert created_organization["building_id"] == building_id
    assert created_organization["activity_ids"] == activity_ids


async def test_create_organization_with_nonexistent_building(
    postgres,
    activity_food,
):
    name = "Organization"
    building_id = 0
    activity_ids = [activity_food["id"]]

    with pytest.raises(application.models.BuildingDoesNotExist):
        await application.models.organization_create(
            postgres,
            name=name,
            building_id=building_id,
            activity_ids=activity_ids,
        )


async def test_create_organization_with_nonexistent_activity(
    postgres,
    building_moscow_a,
):
    name = "Organization"
    building_id = building_moscow_a["id"]
    activity_ids = [0]

    with pytest.raises(application.models.ActivityDoesNotExist):
        await application.models.organization_create(
            postgres,
            name=name,
            building_id=building_id,
            activity_ids=activity_ids,
        )


async def test_create_organization_with_no_activities(
    postgres,
    building_moscow_a,
):
    name = "Organization"
    building_id = building_moscow_a["id"]
    activity_ids = []

    with pytest.raises(application.models.OrganizationActivitiesNotProvided):
        await application.models.organization_create(
            postgres,
            name=name,
            building_id=building_id,
            activity_ids=activity_ids,
        )


async def test_get_organization(postgres, organization_moscow_a_meat):
    fetched_organization = await application.models.organization_get_by_id(
        postgres,
        organization_moscow_a_meat["id"],
    )
    assert fetched_organization == organization_moscow_a_meat


async def test_get_nonexistent_organization(postgres):
    with pytest.raises(application.models.OrganizationDoesNotExist):
        await application.models.organization_get_by_id(postgres, 0)


async def test_get_organizations(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
):
    fetched_organizations = await application.models.organization_get(postgres)

    assert len(fetched_organizations) == 3
    for organization in [
        organization_moscow_a_meat,
        organization_moscow_b_sausages_parts,
        organization_minsk_a_passenger_cars,
    ]:
        assert organization in fetched_organizations


async def test_get_organizations_by_building_id(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    building_moscow_a,
):
    fetched_organizations = (
        await application.models.organization_get_by_building_id(
            postgres,
            building_moscow_a["id"],
        )
    )

    assert len(fetched_organizations) == 1
    assert fetched_organizations == [organization_moscow_a_meat]
    assert organization_moscow_b_sausages_parts not in fetched_organizations


async def test_get_organizations_by_activity_id(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    activity_meat,
):
    fetched_organizations = (
        await application.models.organization_get_by_activity_id(
            postgres,
            activity_meat["id"],
        )
    )

    assert len(fetched_organizations) == 1
    assert fetched_organizations == [organization_moscow_a_meat]
    assert organization_moscow_b_sausages_parts not in fetched_organizations


async def test_get_organizations_by_nested_activities(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    activity_food,
):
    fetched_organizations = (
        await application.models.organization_get_by_nested_activities(
            postgres,
            activity_food["id"],
        )
    )

    # This bit is a bit tricky, because order of activity IDs is not guaranteed
    # and orgamization_moscow_b_sausage_parts has two activities listed.
    assert len(fetched_organizations) == 2
    required_organization_ids = [
        organization["id"]
        for organization in [
            organization_moscow_a_meat,
            organization_moscow_b_sausages_parts,
        ]
    ]
    for required_organization_id in required_organization_ids:
        assert any(
            required_organization_id == organization["id"]
            for organization in fetched_organizations
        )

    assert organization_minsk_a_passenger_cars not in fetched_organizations


async def test_get_organizations_within_tiny_radius(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    building_moscow_a,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 10  # 10 meters

    fetched_organizations = (
        await application.models.organization_get_within_radius(
            postgres,
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius,
        )
    )

    assert fetched_organizations == [organization_moscow_a_meat]


async def test_get_organizations_within_medium_radius(
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
        await application.models.organization_get_within_radius(
            postgres,
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius,
        )
    )

    assert len(fetched_organizations) == 2

    for organization in [
        organization_moscow_a_meat,
        organization_moscow_b_sausages_parts,
    ]:
        assert organization in fetched_organizations

    assert organization_minsk_a_passenger_cars not in fetched_organizations


async def test_get_organizations_within_big_radius(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    building_moscow_a,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 5000 * 1000  # 5000 kilometers

    fetched_organizations = (
        await application.models.organization_get_within_radius(
            postgres,
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius,
        )
    )

    assert len(fetched_organizations) == 3
    for organization in [
        organization_moscow_a_meat,
        organization_moscow_b_sausages_parts,
        organization_minsk_a_passenger_cars,
    ]:
        assert organization in fetched_organizations


async def test_search_organizations(
    postgres,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    organization_minsk_b_buses,
):
    found_organizations = await application.models.organization_search(
        postgres,
        "говядина",
    )

    assert len(found_organizations) == 1
    assert found_organizations[0]["id"] == organization_moscow_a_meat["id"]

    found_organizations = await application.models.organization_search(
        postgres,
        "авто",
    )

    assert len(found_organizations) == 2
    for organization in [
        organization_minsk_a_passenger_cars,
        organization_minsk_b_buses,
    ]:
        assert organization in found_organizations

    found_organizations = await application.models.organization_search(
        postgres,
        "ничего",
    )
    assert len(found_organizations) == 0


async def test_delete_organization(
    postgres,
    organization_moscow_a_meat,
):
    await application.models.organization_delete(
        postgres,
        organization_moscow_a_meat["id"],
    )

    with pytest.raises(application.models.OrganizationDoesNotExist):
        await application.models.organization_get_by_id(
            postgres,
            organization_moscow_a_meat["id"],
        )
