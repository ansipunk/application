async def test_create_activity(api_client):
    name = "Name"
    parent_id = None

    resp = api_client.post(
        "/api/activities/",
        json={
            "name": name,
            "parent_id": parent_id,
        },
    )

    assert resp.status_code == 200

    created_activity = resp.json()
    assert created_activity["id"] is not None
    assert created_activity["level"] is not None
    assert created_activity["name"] == name
    assert created_activity["parent_id"] == parent_id


async def test_create_activity_with_nonexistent_parent_activity(api_client):
    resp = api_client.post(
        "/api/activities/",
        json={
            "name": "Name",
            "parent_id": 0,
        },
    )
    assert resp.status_code == 400


async def test_create_activity_with_exceeded_nesting_limit(
    api_client,
    activity_sausages,
):
    resp = api_client.post(
        "/api/activities/",
        json={
            "name": "Name",
            "parent_id": activity_sausages["id"],
        },
    )
    assert resp.status_code == 400


async def test_get_activities(
    api_client,
    activity_food,
    activity_meat,
    activity_sausages,
):
    resp = api_client.get("/api/activities/")
    assert resp.status_code == 200
    assert resp.json() == {
        "activities": [activity_food, activity_meat, activity_sausages],
    }


async def test_get_activity_by_id(api_client, activity_food):
    resp = api_client.get(f"/api/activities/{activity_food['id']}")
    assert resp.status_code == 200
    assert resp.json() == activity_food


async def test_get_nonexistent_activity(api_client):
    resp = api_client.get("/api/activities/0")
    assert resp.status_code == 404


async def test_delete_activity(api_client, activity_food):
    resp = api_client.delete(f"/api/activities/{activity_food['id']}")
    assert resp.status_code == 200


async def test_delete_activity_with_entities(
    api_client,
    activity_food,
    activity_meat,
):
    resp = api_client.delete(f"/api/activities/{activity_food['id']}")
    assert resp.status_code == 400
