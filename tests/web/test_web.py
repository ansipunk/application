import fastapi.testclient

import application.web


async def test_lifespan(mocker):
    postgres_connect = mocker.patch("application.web.postgres.connect")
    postgres_disconnect = mocker.patch("application.web.postgres.disconnect")

    async with application.web.lifespan(None):
        postgres_connect.assert_called_once()

    postgres_disconnect.assert_called_once()


def test_redirect_to_docs(api_client):
    response = api_client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"] == "/docs"


def test_unauthenticated_api_client():
    client = fastapi.testclient.TestClient(
        application.web.app,
        headers={"X-Application-API-Key": "invalid_key"},
    )
    response = client.get("/api/buildings/")
    assert response.status_code == 403
