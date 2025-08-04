import datetime
from pydantic import BaseModel, validator
from typing import Union, List

from ...enums.rules_enum import RolesEnum, RulesEnum

class InvitationCreateDto(BaseModel):
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    email: str = None
    team_id: str = None
    specie_id: str = None
    ideogram_id: str = None
    folder_id: str = None
    address_id: str = None
    kariotype_id: str = None
    send_mail: bool = None
    roles: List[str] = []
    rules: List[str] = []

    @validator('roles', each_item=True)
    def validate_roles(cls, v):
        if v not in RolesEnum._value2member_map_:
            raise ValueError(f"Invalid role: {v}")
        return v

    @validator('rules', each_item=True)
    def validate_rules(cls, v):
        if v not in RulesEnum._value2member_map_:
            raise ValueError(f"Invalid rule: {v}")
        return v

class InvitationUpdateDto(BaseModel):
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    email: str = None
    team_id: str = None
    specie_id: str = None
    ideogram_id: str = None
    folder_id: str = None
    kariotype_id: str = None
    address_id: str = None
    send_mail: bool = None
    roles: List[str] = []
    rules: List[str] = []
    modified_by_user: str = None
    modified_at: datetime.datetime = None

    @validator('roles', each_item=True)
    def validate_roles(cls, v):
        if v not in RolesEnum._value2member_map_:
            raise ValueError(f"Invalid role: {v}")
        return v

    @validator('rules', each_item=True)
    def validate_rules(cls, v):
        if v not in RulesEnum._value2member_map_:
            raise ValueError(f"Invalid rule: {v}")
        return v

class InvitationDto(BaseModel):
    actived: bool = None
    revoked: bool = None
    owner_user_id: str = None
    guest_user_id: str = None
    email: str = None
    team_id: str = None
    specie_id: str = None
    ideogram_id: str = None
    folder_id: str = None
    kariotype_id: str = None
    address_id: str = None
    send_mail: bool = None
    roles: List[str] = []
    rules: List[str] = []
    actived_at: datetime.datetime = None
    deactived_at: datetime.datetime = None
    modified_by_user: str = None
    modified_at: datetime.datetime = None

    @validator('roles', each_item=True)
    def validate_roles(cls, v):
        if v not in RolesEnum._value2member_map_:
            raise ValueError(f"Invalid role: {v}")
        return v

    @validator('rules', each_item=True)
    def validate_rules(cls, v):
        if v not in RulesEnum._value2member_map_:
            raise ValueError(f"Invalid rule: {v}")
        return v

    class Config:
      orm_mode = True
