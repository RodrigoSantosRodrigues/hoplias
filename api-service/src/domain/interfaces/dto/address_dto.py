import datetime
from pydantic import BaseModel


class AddressDto(BaseModel):
  name: str
  zip_code: str
  street: str = None
  number: int = None
  neighborhood: str = None
  state: str = None
  city: str = None
  complement: str = None
  latitude: str = None
  longitude: str = None
  country: str = None
  user_id: str = None
  team_id: str = None
  specie_id: str = None
  ideogram_id: str = None
  folder_id: str = None
  volunteer_id: str = None
  kariotype_id: str = None
  created_by_user: str = None


class AddressGroupDto(BaseModel):
  address_id: str
  team_id: str = None
  user_id: str = None
  specie_id: str = None
  ideogram_id: str = None
  folder_id: str = None
  volunteer_id: str = None
  kariotype_id: str = None
  created_by_user: str = None

class UpdateDto(BaseModel):
  name: str = None
  zip_code: str = None
  street: str = None
  number: int = None
  neighborhood: str = None
  state: str = None
  city: str = None
  complement: str = None
  latitude: str = None
  longitude: str = None
  country: str = None
  team_id: str = None
  user_id: str = None
  specie_id: str = None
  ideogram_id: str = None
  folder_id: str = None
  volunteer_id: str = None
  kariotype_id: str = None
  modified_by_user: str = None
  modified_at: datetime.datetime = None
