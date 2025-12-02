import datetime
from pydantic import BaseModel, field_validator
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

    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v):
        if isinstance(v, list):
            for item in v:
                if item not in RolesEnum._value2member_map_:
                    raise ValueError(f"Invalid role: {item}")
        return v

    @field_validator('rules')
    @classmethod
    def validate_rules(cls, v):
        if isinstance(v, list):
            for item in v:
                if item not in RulesEnum._value2member_map_:
                    raise ValueError(f"Invalid rule: {item}")
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

    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v):
        if isinstance(v, list):
            for item in v:
                if item not in RolesEnum._value2member_map_:
                    raise ValueError(f"Invalid role: {item}")
        return v

    @field_validator('rules')
    @classmethod
    def validate_rules(cls, v):
        if isinstance(v, list):
            for item in v:
                if item not in RulesEnum._value2member_map_:
                    raise ValueError(f"Invalid rule: {item}")
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

    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v):
        if isinstance(v, list):
            for item in v:
                if item not in RolesEnum._value2member_map_:
                    raise ValueError(f"Invalid role: {item}")
        return v

    @field_validator('rules')
    @classmethod
    def validate_rules(cls, v):
        if isinstance(v, list):
            for item in v:
                if item not in RulesEnum._value2member_map_:
                    raise ValueError(f"Invalid rule: {item}")
        return v

    class Config:
      from_attributes = True
