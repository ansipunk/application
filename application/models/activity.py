import based
import psycopg.errors
import sqlalchemy

from ..core import postgres


class ActivityDoesNotExist(Exception):
    pass


class ActivityNestingLimitReached(Exception):
    pass


class ActivityHasEntities(Exception):
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

    # This is done within a transaction to prevent a race condition
    # where the parent activity was fetched, but got deleted before
    # the child activity was actually created.
    async with session.transaction():
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


async def activity_delete(session: based.Session, activity_id: int):
    query = Activity.delete().where(Activity.c.id == activity_id)

    try:
        await session.execute(query)
    except psycopg.errors.ForeignKeyViolation as e:
        raise ActivityHasEntities from e
