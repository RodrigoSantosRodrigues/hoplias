import datetime
from pydantic import BaseModel
from typing import Union, List
from ...enums.rules_enum import RolesEnum


class CreateFolderDto(BaseModel):
  name: str = None
  description: str = None
  slug: str = None
  team_id: str = None
  folder_parent_id: str = None
  categories: List[str] = []
  categories_name: List[str] = []
  address_id: str = None
  user_id: str = None
  created_by_user: str = None

  class Config:
    orm_mode = True

class UpdateFolderDto(BaseModel):
  name: str = None
  description: str = None
  slug: str = None
  team_id: str = None
  folder_parent_id: str = None
  categories: List[str] = []
  categories_name:  List[str] = []
  address_id: str = None
  user_id: str = None
  modified_by_user: str = None
  modified_at: datetime.datetime = None
