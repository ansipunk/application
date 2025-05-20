import fastapi.testclient
import pytest

import application.web


@pytest.fixture
def api_client(postgres):
    return fastapi.testclient.TestClient(application.web.app)
