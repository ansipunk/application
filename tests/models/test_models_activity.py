import pytest

import application.models


async def test_create_activity(postgres):
    name = "Entertainment"
    parent_id = None
    level = 1

    created_activity = await application.models.activity_create(
        postgres,
        name=name,
        parent_id=parent_id,
    )

    assert created_activity is not None
    assert created_activity["id"] is not None
    assert created_activity["name"] == name
    assert created_activity["parent_id"] == parent_id
    assert created_activity["level"] == level


async def test_create_activity_with_nonexistent_parent_id(postgres):
    with pytest.raises(application.models.ActivityDoesNotExist):
        await application.models.activity_create(
            postgres,
            name="Name",
            parent_id=0,
        )


async def test_create_activity_with_parent(postgres, activity_food):
    name = "Десерты"
    parent_id = activity_food["id"]
    level = activity_food["level"] + 1

    created_activity = await application.models.activity_create(
        postgres,
        name=name,
        parent_id=parent_id,
    )

    assert created_activity is not None
    assert created_activity["id"] is not None
    assert created_activity["name"] == name
    assert created_activity["parent_id"] == parent_id
    assert created_activity["level"] == level


async def test_create_activity_with_exceeded_nesting_level(
    postgres,
    activity_sausages,
):
    name = "Колбасы"
    parent_id = activity_sausages["id"]

    with pytest.raises(application.models.ActivityNestingLimitReached):
        await application.models.activity_create(
            postgres,
            name=name,
            parent_id=parent_id,
        )


async def test_get_activity_by_id(postgres, activity_food):
    fetched_activity = await application.models.activity_get_by_id(
        postgres,
        activity_food["id"],
    )

    assert fetched_activity["id"] == activity_food["id"]
    assert fetched_activity["name"] == activity_food["name"]
    assert fetched_activity["parent_id"] == activity_food["parent_id"]
    assert fetched_activity["level"] == activity_food["level"]


async def test_get_nonexistent_activity(postgres):
    with pytest.raises(application.models.ActivityDoesNotExist):
        await application.models.activity_get_by_id(postgres, 0)


async def test_get_activities(
    postgres,
    activity_food,
    activity_meat,
    activity_sausages,
    activity_vehicles,
    activity_passenger_cars,
    activity_parts,
):
    fetched_activities = await application.models.activity_get(postgres)
    assert len(fetched_activities) == 6

    for activity in [
        activity_food,
        activity_meat,
        activity_sausages,
        activity_vehicles,
        activity_passenger_cars,
        activity_parts,
    ]:
        assert activity in fetched_activities


async def test_delete_activity(postgres, activity_food):
    await application.models.activity_delete(postgres, activity_food["id"])

    with pytest.raises(application.models.ActivityDoesNotExist):
        await application.models.activity_get_by_id(
            postgres,
            activity_food["id"],
        )


async def test_delete_activity_with_child_activities(
    postgres,
    activity_food,
    activity_meat,
):
    with pytest.raises(application.models.ActivityHasEntities):
        await application.models.activity_delete(postgres, activity_food["id"])


async def test_delete_activity_with_organizations(
    postgres,
    activity_meat,
    organization_moscow_a_meat,
):
    with pytest.raises(application.models.ActivityHasEntities):
        await application.models.activity_delete(postgres, activity_meat["id"])
