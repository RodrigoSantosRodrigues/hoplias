import datetime
from pydantic import BaseModel
from typing import List, Union
from ...enums.rules_enum import RolesEnum, RulesEnum


class UserDto(BaseModel):
  name: Union[str, None] = None
  email: Union[str, None] = None
  password: Union[str, None] = None
  cpf_cnpj: Union[str, None] = None
  code_country: Union[str, None] = None
  phone: Union[str, None] = None
  org_name: Union[str, None] = None
  active: Union[bool, None] = None
  actived_at:  Union[datetime.datetime, None] = None
  deactived_at: Union[datetime.datetime, None] = None
  team_id: Union[str, None] = None
  chatbot_user_id: Union[str, None] = None
  created_by_user: Union[str, None] = None
  modified_by_user: Union[str, None] = None
  modified_at: Union[datetime.datetime, None] = None


class UserRecoverDto(BaseModel):
  user_id: Union[str, None] = None
  old_password: Union[str, None] = None
  code: Union[str, None] = None
  expiration_in_days: Union[int, None] = None
  expiration_date: Union[datetime.datetime, None] = None
  message_id: Union[str, None] = None
  validated: Union[bool, None] = None
  actived_at: Union[datetime.datetime, None] = None
  created_by_user: Union[str, None] = None
  modified_by_user: Union[str, None] = None
  modified_at: Union[datetime.datetime, None] = None
