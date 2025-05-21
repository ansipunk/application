import based
import sqlalchemy

from ..core import postgres


class ActivityDoesNotExist(Exception):
    pass


class ActivityNestingLimitReached(Exception):
    pass


Activity = sqlalchemy.Table(
    "activity",
    postgres.metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(
        "parent_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("activity.id"),
        nullable=True,
    ),
    sqlalchemy.Column(
        "level",
        sqlalchemy.Integer,
        nullable=False,
        server_default=sqlalchemy.text("1"),
    ),
)


async def activity_create(
    session: based.Session,
    *,
    name: str,
    parent_id: int | None = None,
):
    nesting_level = 1

    if parent_id is not None:
        parent = await activity_get_by_id(session, parent_id)
        if parent["level"] >= 3:
            raise ActivityNestingLimitReached
        nesting_level = parent["level"] + 1

    query = (
        Activity.insert()
        .values(name=name, parent_id=parent_id, level=nesting_level)
        .returning(*Activity.c)
    )

    # It's very unlikely we will get a foreign key violation here, as we check
    # presence of requested parent activity above. This race condition is almost
    # impossible (completely impossible, if you consider that there is no method
    # for deleting activities yet), so there is no reason to catch it.
    return await session.fetch_one(query)


async def activity_get_by_id(session: based.Session, activity_id: int):
    query = Activity.select().where(Activity.c.id == activity_id)
    activity = await session.fetch_one(query)
    if not activity:
        raise ActivityDoesNotExist
    return activity


async def activity_get(session: based.Session):
    query = Activity.select()
    return await session.fetch_all(query)
