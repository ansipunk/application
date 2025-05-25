import based
import psycopg.errors
import shapely
import sqlalchemy
import sqlalchemy.dialects.postgresql

from ..core import postgres
from .activity import Activity
from .activity import ActivityDoesNotExist
from .building import Building
from .building import BuildingDoesNotExist


class OrganizationDoesNotExist(Exception):
    pass


class OrganizationActivitiesNotProvided(Exception):
    pass


Organization = sqlalchemy.Table(
    "organization",
    postgres.metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(
        "building_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("building.id"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "name_fts",
        sqlalchemy.dialects.postgresql.TSVECTOR,
        sqlalchemy.Computed(
            sqltext="to_tsvector('russian', name)",
            persisted=True,
        ),
        nullable=False,
    ),
    sqlalchemy.Index(
        "ix_organization_name_fts",
        "name_fts",
        postgresql_using="gin",
    ),
    sqlalchemy.Index(
        "ix_organization_name_trgm",
        "name",
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    ),
)

OrganizationActivity = sqlalchemy.Table(
    "organization_activity",
    postgres.metadata,
    sqlalchemy.Column(
        "organization_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("organization.id"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "activity_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("activity.id"),
        nullable=False,
    ),
    sqlalchemy.PrimaryKeyConstraint("organization_id", "activity_id"),
)

OrganizationPhoneNumber = sqlalchemy.Table(
    "organization_phone_number",
    postgres.metadata,
    sqlalchemy.Column(
        "organization_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("organization.id"),
        nullable=False,
    ),
    sqlalchemy.Column("phone_number", sqlalchemy.Text, nullable=False),
)


async def organization_create(
    session: based.Session,
    *,
    name: str,
    building_id: int,
    phone_numbers: list[str],
    activity_ids: list[int],
):
    if not activity_ids:
        raise OrganizationActivitiesNotProvided

    # We run this in a transaction, so if a nonexistent activity ID is used,
    # the organization is not created.
    async with session.transaction():
        query = (
            Organization.insert()
            .values(
                name=name,
                building_id=building_id,
            )
            .returning(
                Organization.c.id,
                Organization.c.name,
                Organization.c.building_id,
            )
        )

        try:
            organization = await session.fetch_one(query)
        except psycopg.errors.ForeignKeyViolation as e:
            raise BuildingDoesNotExist from e

        # De-duplicate activities and phone numbers
        activity_ids = set(activity_ids)
        phone_numbers = set(phone_numbers)

        organization_activity_rows = []
        for activity_id in activity_ids:
            organization_activity_rows.append(
                {
                    "organization_id": organization["id"],
                    "activity_id": activity_id,
                },
            )

        query = OrganizationActivity.insert().values(organization_activity_rows)

        try:
            await session.execute(query)
        except psycopg.errors.ForeignKeyViolation as e:
            raise ActivityDoesNotExist from e

        organization_phone_number_rows = []
        for phone_number in phone_numbers:
            organization_phone_number_rows.append(
                {
                    "organization_id": organization["id"],
                    "phone_number": phone_number,
                },
            )

        query = OrganizationPhoneNumber.insert().values(
            organization_phone_number_rows,
        )
        await session.execute(query)

        organization["activity_ids"] = list(activity_ids)
        organization["phone_numbers"] = list(phone_numbers)
        return organization


def _get_organization_query():
    return (
        Organization.select()
        .with_only_columns(
            Organization.c.id,
            Organization.c.name,
            Organization.c.building_id,
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(OrganizationActivity.c.activity_id),
            )
            .filter(OrganizationActivity.c.activity_id.isnot(None))
            .label("activity_ids"),
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(OrganizationPhoneNumber.c.phone_number),
            )
            .filter(OrganizationPhoneNumber.c.phone_number.isnot(None))
            .label("phone_numbers"),
        )
        .select_from(
            Organization.join(
                OrganizationPhoneNumber,
                Organization.c.id == OrganizationPhoneNumber.c.organization_id,
            ).join(
                OrganizationActivity,
                Organization.c.id == OrganizationActivity.c.organization_id,
            ),
        )
        .group_by(Organization.c.id, Organization.c.name)
    )


async def organization_get_by_id(session: based.Session, organization_id: int):
    query = _get_organization_query().where(
        Organization.c.id == organization_id,
    )
    organization = await session.fetch_one(query)
    if organization is None:
        raise OrganizationDoesNotExist
    return organization


async def organization_get(session: based.Session):
    query = _get_organization_query()
    return await session.fetch_all(query)


async def organization_get_by_building_id(
    session: based.Session,
    building_id: int,
):
    query = _get_organization_query().where(
        Organization.c.building_id == building_id,
    )
    return await session.fetch_all(query)


async def organization_get_by_activity_id(
    session: based.Session,
    activity_id: int,
):
    query = _get_organization_query().having(
        sqlalchemy.func.bool_or(
            OrganizationActivity.c.activity_id == activity_id,
        ),
    )
    return await session.fetch_all(query)


async def organization_get_by_nested_activities(
    session: based.Session,
    activity_id: int,
):
    activities = Activity.alias("a")
    p1 = sqlalchemy.alias(Activity, name="p1")
    p2 = sqlalchemy.alias(Activity, name="p2")
    oa = OrganizationActivity.alias("oa")
    on = OrganizationPhoneNumber.alias("on")
    o = Organization.alias("o")

    # First of all, we need to find all the activities that
    # are in the subtree of requested activity.
    activity_ids_cte = (
        sqlalchemy.select(activities.c.id)
        .outerjoin(p1, activities.c.parent_id == p1.c.id)
        .outerjoin(p2, p1.c.parent_id == p2.c.id)
        .where(
            sqlalchemy.or_(
                activities.c.id == activity_id,
                activities.c.parent_id == activity_id,
                p1.c.parent_id == activity_id,
            ),
        )
        .cte("matched_activities")
    )

    # Then we find organizations that have those activities listed.
    matching_org_ids = (
        sqlalchemy.select(oa.c.organization_id)
        .where(oa.c.activity_id.in_(sqlalchemy.select(activity_ids_cte.c.id)))
        .distinct()
        .cte("matched_orgs")
    )

    # And, finally, fetch all the matching organizations and their activities,
    # even if they are not within the requested activity tree.
    query = (
        sqlalchemy.select(
            o.c.id,
            o.c.name,
            o.c.building_id,
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(oa.c.activity_id),
            )
            .filter(oa.c.activity_id.isnot(None))
            .label("activity_ids"),
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(on.c.phone_number),
            )
            .filter(on.c.phone_number.isnot(None))
            .label("phone_numbers"),
        )
        .join(on, o.c.id == on.c.organization_id)
        .join(oa, o.c.id == oa.c.organization_id)
        .join(matching_org_ids, matching_org_ids.c.organization_id == o.c.id)
        .group_by(o.c.id, o.c.name)
    )

    return await session.fetch_all(query)


async def organization_get_within_radius(
    session: based.Session,
    *,
    longitude: float,
    latitude: float,
    radius_meters: float,
):
    b = Building.alias("b")
    o = Organization.alias("o")
    oa = OrganizationActivity.alias("oa")
    on = OrganizationPhoneNumber.alias("on")

    point = shapely.Point(longitude, latitude).wkt

    query = (
        sqlalchemy.select(
            o.c.id,
            o.c.name,
            o.c.building_id,
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(oa.c.activity_id),
            )
            .filter(oa.c.activity_id.isnot(None))
            .label("activity_ids"),
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(on.c.phone_number),
            )
            .filter(on.c.phone_number.isnot(None))
            .label("phone_numbers"),
        )
        .join(b, o.c.building_id == b.c.id)
        .join(on, o.c.id == on.c.organization_id)
        .join(oa, o.c.id == oa.c.organization_id)
        .where(
            sqlalchemy.text(
                "ST_DWithin(b.location::geography, "
                f"ST_SetSRID(ST_GeomFromText('{point}'),"
                f" 4326)::geography, {radius_meters})",
            ),
        )
        .group_by(o.c.id, o.c.name)
    )

    return await session.fetch_all(query)


async def organization_search(session: based.Session, search_text: str):
    o = Organization.alias("o")
    oa = OrganizationActivity.alias("oa")
    on = OrganizationPhoneNumber.alias("on")

    ts_query = sqlalchemy.func.plainto_tsquery(
        sqlalchemy.text("'russian'"),
        search_text,
    )
    rank = sqlalchemy.func.ts_rank_cd(o.c.name_fts, ts_query)
    similarity_score = sqlalchemy.func.similarity(o.c.name, search_text)

    query = (
        sqlalchemy.select(
            o.c.id,
            o.c.name,
            o.c.building_id,
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(oa.c.activity_id),
            )
            .filter(oa.c.activity_id.isnot(None))
            .label("activity_ids"),
            sqlalchemy.dialects.postgresql.array_agg(
                sqlalchemy.distinct(on.c.phone_number),
            )
            .filter(on.c.phone_number.isnot(None))
            .label("phone_numbers"),
            rank.label("rank"),
            similarity_score.label("similarity"),
        )
        .join(on, o.c.id == on.c.organization_id)
        .join(oa, oa.c.organization_id == o.c.id)
        .where((o.c.name_fts.op("@@")(ts_query)) | (similarity_score > 0.3))
        .group_by(o.c.id, o.c.name)
        .order_by(
            rank.desc(),
            similarity_score.desc(),
        )
    )

    results = await session.fetch_all(query)
    for result in results:
        del result["rank"]
        del result["similarity"]
    return results


async def organization_delete(session: based.Session, organization_id: int):
    query = OrganizationActivity.delete().where(
        OrganizationActivity.c.organization_id == organization_id,
    )
    await session.execute(query)

    query = OrganizationPhoneNumber.delete().where(
        OrganizationPhoneNumber.c.organization_id == organization_id,
    )
    await session.execute(query)

    query = Organization.delete().where(Organization.c.id == organization_id)
    await session.execute(query)
