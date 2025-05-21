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


@pytest.fixture
def activity(postgres):
    async def builder(name, parent_id=None):
        return await application.models.activity_create(
            postgres,
            name=name,
            parent_id=parent_id,
        )

    return builder


@pytest.fixture
async def activity_food(activity):
    return await activity("Еда")


@pytest.fixture
async def activity_meat(activity, activity_food):
    return await activity("Мясная продукция", activity_food["id"])


@pytest.fixture
async def activity_sausages(activity, activity_meat):
    return await activity("Колбасы и сосиски", activity_meat["id"])


@pytest.fixture
async def activity_vehicles(activity):
    return await activity("Автомобили")


@pytest.fixture
async def activity_passenger_cars(activity, activity_vehicles):
    return await activity(
        "Легковые автомобили",
        parent_id=activity_vehicles["id"],
    )


@pytest.fixture
async def activity_parts(activity, activity_passenger_cars):
    return await activity(
        "Запчасти",
        parent_id=activity_passenger_cars["id"],
    )


@pytest.fixture
def organization(postgres):
    async def builder(name, building_id, activity_ids, phone_number=None):
        return await application.models.organization_create(
            postgres,
            name=name,
            phone_number=phone_number,
            building_id=building_id,
            activity_ids=activity_ids,
        )

    return builder


@pytest.fixture
async def organization_moscow_a_meat(
    organization,
    building_moscow_a,
    activity_meat,
):
    return await organization(
        "Только говядина",
        building_moscow_a["id"],
        [activity_meat["id"]],
        "8 800 555 3535",
    )


@pytest.fixture
async def organization_moscow_b_sausages_parts(
    organization,
    building_moscow_b,
    activity_sausages,
    activity_parts,
):
    return await organization(
        "Шаурма и аккумуляторы",
        building_moscow_b["id"],
        [activity_sausages["id"], activity_parts["id"]],
        "+7 915 111 2233",
    )


@pytest.fixture
async def organization_minsk_a_passenger_cars(
    organization,
    building_minsk_a,
    activity_passenger_cars,
):
    return await organization(
        "Автосалон",
        building_minsk_a["id"],
        [activity_passenger_cars["id"]],
        "+375 44 123 4567",
    )


@pytest.fixture
async def organization_minsk_b_buses(
    organization,
    building_minsk_b,
    activity_passenger_cars,
):
    return await organization(
        "Автобусы",
        building_minsk_b["id"],
        [activity_passenger_cars["id"]],
        "+375 33 420 1337",
    )
