import datetime
from pydantic import BaseModel
from typing import Union, List

class GrantCreateDto(BaseModel):
    invitation_id: str
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    restrict_folders: List[str] = []
    roles: List[str] = []
    rules: List[str] = []
    team_id: str = None

class GrantUpdateDto(BaseModel):
    invitation_id: str
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    restrict_folders: List[str] = []
    roles: List[str] = []
    rules: List[str] = []
    team_id: str = None
    modified_by_user: str = None
    modified_at: datetime.datetime = None

class GrantDto(BaseModel):
    invitation_id: str
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    restrict_folders: List[str] = []
    roles: List[str] = []
    rules: List[str] = []
    team_id: str = None
    actived_at: datetime.datetime = None
    deactived_at: datetime.datetime = None
    modified_by_user: str = None
    modified_at: datetime.datetime = None

    class Config:
      orm_mode = True
