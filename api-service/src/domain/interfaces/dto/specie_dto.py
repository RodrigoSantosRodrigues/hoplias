import datetime
from pydantic import BaseModel
from typing import List, Union


class SpecieDto(BaseModel):
  name: str
  slug_name: str = None
  scientific_name: str
  family: str
  description: Union[str, None] = None
  habitat: Union[str, None] = None
  endangered: bool = False
  conservation_status: Union[str, None] = None
  common_names: List[str] = []
  external_id: Union[str, None] = None
  location_id: Union[str, None] = None
  user_id: str = None
  team_id: str = None
  created_by_user: Union[str, None] = None

  class Config:
    orm_mode = True


class UpdateDto(BaseModel):
  name: Union[str, None] = None
  slug_name: str = None
  scientific_name: Union[str, None] = None
  family: Union[str, None] = None
  description: Union[str, None] = None
  habitat: Union[str, None] = None
  endangered: Union[bool, None] = None
  conservation_status: Union[str, None] = None
  common_names: List[str] = []
  external_id: Union[str, None] = None
  location_id: Union[str, None] = None
  user_id: Union[str, None] = None
  team_id: Union[str, None] = None
  modified_by_user: Union[str, None] = None
  modified_at: Union[datetime.datetime, None] = None

  class Config:
    orm_mode = True
