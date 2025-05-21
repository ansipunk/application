import fastapi
import pytest

import application.models
import application.web.controllers
import application.web.schemas


async def test_create_activity(mocker, postgres):
    name = "Name"
    parent_id = None

    activity = application.web.schemas.ActivityCreate(
        name=name,
        parent_id=parent_id,
    )

    model_mock = mocker.spy(application.models, "activity_create")

    created_activity = await application.web.controllers.activity_create(
        postgres,
        activity,
    )

    assert created_activity == model_mock.spy_return
    model_mock.assert_called_once_with(
        postgres,
        name=name,
        parent_id=parent_id,
    )


async def test_create_activity_with_nesting_limit_reached(
    postgres,
    activity_sausages,
):
    activity = application.web.schemas.ActivityCreate(
        name="Name",
        parent_id=activity_sausages["id"],
    )

    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.activity_create(postgres, activity)

    assert e.value.status_code == 400


async def test_get_activity_by_id(postgres, activity_food):
    fetched_activity = await application.web.controllers.activity_get_by_id(
        postgres,
        activity_food["id"],
    )
    assert fetched_activity == activity_food


async def test_get_nonexistent_activity(postgres):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.activity_get_by_id(postgres, 0)

    assert e.value.status_code == 404


async def test_get_activities(postgres, activity_food, activity_meat):
    fetched_activities = await application.web.controllers.activity_get(
        postgres,
    )
    assert fetched_activities == {"activities": [activity_food, activity_meat]}


async def test_delete_activity(mocker, postgres, activity_food):
    model_mock = mocker.spy(application.models, "activity_delete")
    await application.web.controllers.activity_delete(
        postgres,
        activity_food["id"],
    )
    model_mock.assert_called_once_with(postgres, activity_food["id"])


async def test_delete_activity_with_entities(
    postgres,
    activity_food,
    activity_meat,
):
    with pytest.raises(fastapi.HTTPException) as e:
        await application.web.controllers.activity_delete(
            postgres,
            activity_food["id"],
        )

    assert e.value.status_code == 400
