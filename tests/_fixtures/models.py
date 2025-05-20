import pytest

import application.models


@pytest.fixture
def building(postgres):
    async def builder(address, longitude, latitude):
        return await application.models.building_create(
            postgres,
            address=address,
            longitude=longitude,
            latitude=latitude,
        )

    return builder


@pytest.fixture
async def building_moscow_a(building):
    return await building(
        "г. Москва, пр-т Вернадского, 87/48",
        55.670539,
        37.497450,
    )


@pytest.fixture
async def building_moscow_b(building):
    return await building(
        "г. Москва, ул. Краснопрудная, 15",
        55.780993,
        37.668067,
    )


@pytest.fixture
async def building_minsk_a(building):
    return await building(
        "г. Минск, пр-т Партизанский, 56/2",
        53.873611,
        27.631442,
    )


@pytest.fixture
async def building_minsk_b(building):
    return await building(
        "г. Минск, ул. Тимирязева, 74",
        53.926340,
        27.510609,
    )
