import typing

import pydantic


class ActivityBase(pydantic.BaseModel):
    name: typing.Annotated[str, pydantic.constr(min_length=1, max_length=50)]
    parent_id: int | None = None


class ActivityCreate(ActivityBase):
    pass


class ActivityGet(ActivityBase):
    level: int


class ActivityGetList(pydantic.BaseModel):
    activities: list[ActivityGet]
