import fastapi.testclient
import pytest

import application.core.config
import application.web


@pytest.fixture
def api_client(postgres):
    return fastapi.testclient.TestClient(
        application.web.app,
        headers={"X-Application-API-Key": application.core.config.web.api_key},
    )
