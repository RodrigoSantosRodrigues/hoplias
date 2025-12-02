import datetime
from pydantic import BaseModel
from typing import Union

class TeamCreateDto(BaseModel):
    name: str = None
    description: str = None
    user_id: str = None
    active: bool = None
    created_by_user: str = None

class TeamUpdateDto(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    user_id: str = None
    active: Union[bool, None] = None
    modified_by_user: Union[str, None] = None
    modified_at: Union[datetime.datetime, None] = None

class TeamDto(BaseModel):
    name: str
    description: str = None
    user_id: str = None
    active: bool = None
    actived_at: datetime.datetime
    deactived_at: datetime.datetime = None

    class Config:
      from_attributes = True
