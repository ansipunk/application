import logging

import psycopg

import application.core.config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    with psycopg.connect(  # noqa: SIM117
        application.core.config.postgres.url,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM building;")

            if cursor.fetchone():
                logger.info("The database is already populated.")
                return

            cursor.execute("""
                INSERT INTO building (address, location)
                VALUES (
                    'г. Москва, пр-т Вернадского, 87/48',
                    ST_SetSRID(ST_MakePoint(37.497450, 55.670539), 4326)
                )
                RETURNING id;
            """)

            building_moscow_a = cursor.fetchone()

            cursor.execute("""
                INSERT INTO building (address, location)
                VALUES (
                    'г. Москва, ул. Краснопрудная, 15',
                    ST_SetSRID(ST_MakePoint(37.668067, 55.780993), 4326)
                )
                RETURNING id;
            """)
            building_moscow_b = cursor.fetchone()

            cursor.execute("""
                INSERT INTO building (address, location)
                VALUES (
                    'г. Минск, пр-т Партизанский, 56/2',
                    ST_SetSRID(ST_MakePoint(27.631442, 53.873611), 4326)
                )
                RETURNING id;
            """)
            building_minsk_a = cursor.fetchone()

            cursor.execute("""
                INSERT INTO building (address, location)
                VALUES (
                    'г. Минск, ул. Тимирязева, 74',
                    ST_SetSRID(ST_MakePoint(27.510609, 53.926340), 4326)
                )
                RETURNING id;
            """)
            building_minsk_b = cursor.fetchone()

            cursor.execute("""
                INSERT INTO activity (name, parent_id, level)
                VALUES (
                    'Еда',
                    NULL,
                    1
                )
                RETURNING id;
            """)
            activity_food = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO activity (name, parent_id, level)
                VALUES (
                    'Мясная продукция',
                    {activity_food[0]},
                    2
                )
                RETURNING id;
            """)
            activity_meat = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO activity (name, parent_id, level)
                VALUES (
                    'Колбасы и сосиски',
                    {activity_meat[0]},
                    3
                )
                RETURNING id;
            """)
            activity_sausages = cursor.fetchone()

            cursor.execute("""
                INSERT INTO activity (name, parent_id, level)
                VALUES (
                    'Автомобили',
                    NULL,
                    1
                )
                RETURNING id;
            """)
            activity_vehicles = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO activity (name, parent_id, level)
                VALUES (
                    'Легковые автомобили',
                    {activity_vehicles[0]},
                    2
                )
                RETURNING id;
            """)
            activity_passenger_cars = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO activity (name, parent_id, level)
                VALUES (
                    'Запчасти',
                    {activity_passenger_cars[0]},
                    3
                )
                RETURNING id;
            """)
            activity_parts = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO organization (name, phone_number, building_id)
                VALUES (
                    'Только говядина',
                    '8 800 555 3535',
                    {building_moscow_a[0]}
                )
                RETURNING id;
            """)
            organization_moscow_a_meat = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO organization_activity (organization_id, activity_id)
                VALUES (
                    {organization_moscow_a_meat[0]},
                    {activity_meat[0]}
                )
            """)

            cursor.execute(f"""
                INSERT INTO organization (name, phone_number, building_id)
                VALUES (
                    'Шаурма и аккумуляторы',
                    '+7 915 111 2233',
                    {building_moscow_b[0]}
                )
                RETURNING id;
            """)
            organization_moscow_b_sausages_parts = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO organization_activity (organization_id, activity_id)
                VALUES (
                    {organization_moscow_b_sausages_parts[0]},
                    {activity_sausages[0]}
                )
            """)
            cursor.execute(f"""
                INSERT INTO organization_activity (organization_id, activity_id)
                VALUES (
                    {organization_moscow_b_sausages_parts[0]},
                    {activity_parts[0]}
                )
            """)

            cursor.execute(f"""
                INSERT INTO organization (name, phone_number, building_id)
                VALUES (
                    'Автосалон',
                    '+375 44 123 4567',
                    {building_minsk_a[0]}
                )
                RETURNING id;
            """)
            organization_minsk_a_passenger_cars = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO organization_activity (organization_id, activity_id)
                VALUES (
                    {organization_minsk_a_passenger_cars[0]},
                    {activity_passenger_cars[0]}
                )
            """)

            cursor.execute(f"""
                INSERT INTO organization (name, phone_number, building_id)
                VALUES (
                    'Автобусы',
                    '+375 33 420 1337',
                    {building_minsk_b[0]}
                )
                RETURNING id;
            """)
            organization_minsk_b_buses = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO organization_activity (organization_id, activity_id)
                VALUES (
                    {organization_minsk_b_buses[0]},
                    {activity_passenger_cars[0]}
                )
            """)

            conn.commit()

    logger.info("Test data added successfully.")


if __name__ == "__main__":
    main()
