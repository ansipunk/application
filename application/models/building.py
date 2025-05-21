import based
import geoalchemy2
import geoalchemy2.shape
import shapely
import shapely.geometry
import sqlalchemy

from ..core import postgres


class BuildingDoesNotExist(Exception):
    pass


Building = sqlalchemy.Table(
    "building",
    postgres.metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("address", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(
        "location",
        geoalchemy2.Geometry(geometry_type="POINT", srid=4326),
        nullable=False,
    ),
)


def _populate_building_lon_lat(building):
    point = shapely.from_wkb(building["location"])
    building["longitude"] = point.x
    building["latitude"] = point.y

    # Have to remove this field for JSON serialization
    # and to not waste any memory.
    del building["location"]

    return building


def _populate_buildings_lon_lat(buildings):
    return list(map(_populate_building_lon_lat, buildings))


async def building_create(
    session: based.Session,
    *,
    address: str,
    longitude: float,
    latitude: float,
):
    # We use shapely to create PostGIS geometry type
    # because manually creating a string is error prone.
    location = shapely.geometry.Point(longitude, latitude).wkt

    query = (
        Building.insert()
        .values(
            address=address,
            location=sqlalchemy.text(
                f"ST_SetSRID(ST_GeomFromText('{location}'), 4326)",
            ),
        )
        .returning(*Building.c)
    )

    building = await session.fetch_one(query)

    # Similarly, we use shapely to get longitude and latitude
    # that were actually saved to the database in case
    # if they were somehow altered.
    return _populate_building_lon_lat(building)


async def building_get_by_id(
    session: based.Session,
    building_id: int,
):
    query = Building.select().where(Building.c.id == building_id)
    building = await session.fetch_one(query)

    if building is None:
        raise BuildingDoesNotExist

    # We need to convert PostGIS geometry type
    # to human understandable longitude/latitude pair.
    # We use shapely because manually parsing text is error prone.
    return _populate_building_lon_lat(building)


async def building_get(session: based.Session):
    query = Building.select()
    buildings = await session.fetch_all(query)
    return _populate_buildings_lon_lat(buildings)


async def building_get_within_radius(
    session: based.Session,
    *,
    origin_longitude: float,
    origin_latitude: float,
    radius_meters: float,
):
    location = shapely.geometry.Point(origin_longitude, origin_latitude).wkt
    query = Building.select().where(
        sqlalchemy.text(f"""ST_DWithin(
            location::geography,
            ST_SetSRID(ST_GeomFromText('{location}'), 4326)::geography,
            {radius_meters}
        )"""),
    )
    buildings = await session.fetch_all(query)
    return _populate_buildings_lon_lat(buildings)
