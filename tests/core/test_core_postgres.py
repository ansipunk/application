import pytest

from application.core import postgres


async def test_connection():
    async def test_session():
        async with postgres.session() as session:
            query = "SELECT 'value' AS key;"
            row = await session.fetch_one(query)
            return row == {"key": "value"}

    with pytest.raises(postgres.PostgresNotConnectedError):
        await test_session()

    await postgres.connect()
    assert await test_session()
    await postgres.disconnect()

    with pytest.raises(postgres.PostgresNotConnectedError):
        await test_session()
