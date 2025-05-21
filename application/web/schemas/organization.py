import typing

import pydantic


class OrganizationBase(pydantic.BaseModel):
    name: typing.Annotated[str, pydantic.constr(min_length=1, max_length=100)]
    building_id: int
    activity_ids: typing.Annotated[
        list[int],
        pydantic.conlist(int, min_length=1),
    ]


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationGet(OrganizationBase):
    id: int


class OrganizationGetList(pydantic.BaseModel):
    organizations: list[OrganizationGet]
