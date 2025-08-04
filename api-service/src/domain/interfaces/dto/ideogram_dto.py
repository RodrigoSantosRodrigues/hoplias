import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Union


class CreateIdeogramDto(BaseModel):
  name: str
  description: Optional[str] = None
  citogenetic_view: Optional[Dict] = None
  citogenomic_view: Optional[Dict] = None
  text_gff: Optional[str] = None
  folder_id: Optional[str] = None
  address_id: Optional[str] = None
  specie_id: Optional[str] = None
  categories: Optional[List[str]] = None
  user_id: str = None
  team_id: str = None
  categories_name: List[str] = []
  created_by_user: Union[str, None] = None
  created_at: Union[datetime.datetime, None] = None

  class Config:
    orm_mode = True

class UpdateIdeogramDto(BaseModel):
  name: Optional[str] = None
  description: Optional[str] = None
  citogenetic_view: Optional[Dict] = None
  citogenomic_view: Optional[Dict] = None
  text_gff: Optional[str] = None
  folder_id: Optional[str] = None
  address_id: Optional[str] = None
  specie_id: Optional[str] = None
  categories: Optional[List[str]] = None
  user_id: str = None
  team_id: str = None
  modified_by_user: Union[str, None] = None
  modified_at: Union[datetime.datetime, None] = None

  class Config:
    orm_mode = True
