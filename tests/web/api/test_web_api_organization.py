async def test_create_organization(
    api_client,
    building_moscow_a,
    activity_food,
):
    name = "Name"
    building_id = building_moscow_a["id"]
    activity_ids = [activity_food["id"]]
    phone_number = "+7 999 666 8888"

    resp = api_client.post(
        "/api/organizations/",
        json={
            "name": name,
            "building_id": building_id,
            "activity_ids": activity_ids,
            "phone_number": phone_number,
        },
    )

    assert resp.status_code == 200

    created_organization = resp.json()
    assert created_organization["id"] is not None
    assert created_organization["name"] == name
    assert created_organization["phone_number"] == phone_number
    assert created_organization["building_id"] == building_id
    assert created_organization["activity_ids"] == activity_ids


async def test_create_organization_with_nonexistent_building_id(
    api_client,
    activity_food,
):
    name = "Name"
    building_id = 0
    activity_ids = [activity_food["id"]]
    phone_number = "+7 999 666 8888"

    resp = api_client.post(
        "/api/organizations/",
        json={
            "name": name,
            "building_id": building_id,
            "activity_ids": activity_ids,
            "phone_number": phone_number,
        },
    )

    assert resp.status_code == 400


async def test_create_organization_with_nonexistent_activity_id(
    api_client,
    building_moscow_a,
):
    name = "Name"
    building_id = building_moscow_a["id"]
    activity_ids = [0]
    phone_number = "+7 999 666 8888"

    resp = api_client.post(
        "/api/organizations/",
        json={
            "name": name,
            "building_id": building_id,
            "activity_ids": activity_ids,
            "phone_number": phone_number,
        },
    )

    assert resp.status_code == 400


async def test_create_organization_with_no_activity_ids(
    api_client,
    building_moscow_a,
):
    name = "Name"
    building_id = building_moscow_a["id"]
    activity_ids = []
    phone_number = "+7 999 666 8888"

    resp = api_client.post(
        "/api/organizations/",
        json={
            "name": name,
            "building_id": building_id,
            "activity_ids": activity_ids,
            "phone_number": phone_number,
        },
    )

    assert resp.status_code == 400


async def test_get_organizations(
    api_client,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
):
    resp = api_client.get("/api/organizations/")
    assert resp.status_code == 200

    expected_organization_ids = {
        organization["id"]
        for organization in [
            organization_moscow_a_meat,
            organization_moscow_b_sausages_parts,
        ]
    }
    fetched_organization_ids = {
        organization["id"] for organization in resp.json()["organizations"]
    }

    assert expected_organization_ids == fetched_organization_ids


async def test_get_organizations_by_building_id(
    api_client,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    building_moscow_a,
):
    resp = api_client.get(
        "/api/organizations/by_building",
        params={"building_id": building_moscow_a["id"]},
    )
    assert resp.status_code == 200
    assert resp.json() == {"organizations": [organization_moscow_a_meat]}


async def test_get_organizations_by_activity_id(
    api_client,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    activity_meat,
):
    resp = api_client.get(
        "/api/organizations/by_activity",
        params={"activity_id": activity_meat["id"]},
    )
    assert resp.status_code == 200
    assert resp.json() == {"organizations": [organization_moscow_a_meat]}


async def test_get_organizations_by_activity_id_include_nested(
    api_client,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    activity_meat,
):
    resp = api_client.get(
        "/api/organizations/by_activity",
        params={"activity_id": activity_meat["id"], "include_nested": True},
    )
    assert resp.status_code == 200

    expected_organization_ids = {
        organization["id"]
        for organization in [
            organization_moscow_a_meat,
            organization_moscow_b_sausages_parts,
        ]
    }
    fetched_organization_ids = {
        organization["id"] for organization in resp.json()["organizations"]
    }

    assert expected_organization_ids == fetched_organization_ids


async def test_get_organizations_by_radius(
    api_client,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    building_moscow_a,
):
    longitude = building_moscow_a["longitude"]
    latitude = building_moscow_a["latitude"]
    radius = 25 * 1000  # 25 kilometers

    resp = api_client.get(
        "/api/organizations/by_radius",
        params={
            "longitude": longitude,
            "latitude": latitude,
            "radius_meters": radius,
        },
    )
    assert resp.status_code == 200

    expected_organization_ids = {
        organization["id"]
        for organization in [
            organization_moscow_a_meat,
            organization_moscow_b_sausages_parts,
        ]
    }
    fetched_organization_ids = {
        organization["id"] for organization in resp.json()["organizations"]
    }

    assert expected_organization_ids == fetched_organization_ids


async def test_search_organizations(
    api_client,
    organization_moscow_a_meat,
    organization_moscow_b_sausages_parts,
    organization_minsk_a_passenger_cars,
    organization_minsk_b_buses,
):
    resp = api_client.get("/api/organizations/search", params={"query": "авто"})
    assert resp.status_code == 200

    expected_organization_ids = {
        organization["id"]
        for organization in [
            organization_minsk_a_passenger_cars,
            organization_minsk_b_buses,
        ]
    }
    found_organization_ids = {
        organization["id"] for organization in resp.json()["organizations"]
    }

    assert expected_organization_ids == found_organization_ids


async def test_get_organization_by_id(
    api_client,
    organization_moscow_a_meat,
):
    resp = api_client.get(
        f"/api/organizations/{organization_moscow_a_meat['id']}",
    )
    assert resp.status_code == 200
    assert resp.json() == organization_moscow_a_meat


async def test_get_nonexistent_organization(api_client):
    resp = api_client.get("/api/organizations/0")
    assert resp.status_code == 404


async def test_delete_organization(api_client, organization_moscow_a_meat):
    resp = api_client.delete(
        f"/api/organizations/{organization_moscow_a_meat['id']}",
    )
    assert resp.status_code == 200
