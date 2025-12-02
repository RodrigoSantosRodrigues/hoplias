import datetime
from pydantic import BaseModel
from typing import Union, List

class ShareCreateDto(BaseModel):
    invitation_id: str
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    roles: List[str] = []
    rules: List[str] = []
    team_id: str = None
    address_id: str = None
    specie_id: str = None
    ideogram_id: str = None
    folder_id: str = None
    kariotype_id: str = None

class ShareUpdateDto(BaseModel):
    invitation_id: str
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    restrict_folders: List[str] = []
    roles: List[str] = []
    rules: List[str] = []
    team_id: str = None
    address_id: str = None
    specie_id: str = None
    ideogram_id: str = None
    folder_id: str = None
    kariotype_id: str = None
    modified_by_user: str = None
    modified_at: datetime.datetime = None

class ShareDto(BaseModel):
    invitation_id: str
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    restrict_folders: List[str] = []
    roles: List[str] = []
    rules: List[str] = []
    team_id: str = None
    address_id: str = None
    specie_id: str = None
    ideogram_id: str = None
    folder_id: str = None
    kariotype_id: str = None
    actived_at: datetime.datetime = None
    deactived_at: datetime.datetime = None
    modified_by_user: str = None
    modified_at: datetime.datetime = None

    class Config:
      from_attributes = True
