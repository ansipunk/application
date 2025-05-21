async def test_create_building(api_client):
    address = "Address"
    longitude = 12.34
    latitude = 56.78

    resp = api_client.post(
        "/api/buildings/",
        json={
            "address": address,
            "longitude": longitude,
            "latitude": latitude,
        },
    )

    assert resp.status_code == 200

    created_building = resp.json()
    assert created_building["id"] is not None
    assert created_building["address"] == address
    assert created_building["longitude"] == longitude
    assert created_building["latitude"] == latitude


async def test_get_buildings(api_client, building_moscow_a, building_minsk_b):
    resp = api_client.get("/api/buildings/")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["buildings"]) == 2


async def test_get_building_by_id(api_client, building_moscow_a):
    resp = api_client.get(f"/api/buildings/{building_moscow_a['id']}")
    assert resp.status_code == 200
    assert resp.json() == building_moscow_a


async def test_get_nonexistent_building(api_client):
    resp = api_client.get("/api/buildings/0")
    assert resp.status_code == 404


async def test_get_buildings_by_radius(
    api_client,
    building_moscow_a,
    building_moscow_b,
    building_minsk_a,
    building_minsk_b,
):
    longitude = building_minsk_a["longitude"]
    latitude = building_minsk_a["latitude"]
    radius = 25 * 1000  # 25 kilometers

    resp = api_client.get(
        "/api/buildings/by_radius",
        params={
            "longitude": longitude,
            "latitude": latitude,
            "radius_meters": radius,
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["buildings"]) == 2


async def test_delete_building(api_client, building_moscow_a):
    resp = api_client.delete(f"/api/buildings/{building_moscow_a['id']}")
    assert resp.status_code == 200
