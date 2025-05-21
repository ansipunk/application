import typing

import pydantic


class BuildingBase(pydantic.BaseModel):
    address: typing.Annotated[
        str,
        pydantic.constr(min_length=1, max_length=100),
    ]
    longitude: float
    latitude: float


class BuildingCreate(BuildingBase):
    pass


class BuildingGet(BuildingBase):
    id: int


class BuildingGetList(pydantic.BaseModel):
    buildings: list[BuildingGet]
