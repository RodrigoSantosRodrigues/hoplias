from bson import ObjectId
from typing import List, Optional

from mongoengine import StringField, BooleanField, ListField, DateTimeField
from datetime import datetime
from .base_model import BaseModel


class UserModel(BaseModel):
  meta = {
    'collection': 'users'
  }

  name = StringField(required=True)
  email = StringField(required=True, unique=True)
  password = StringField(required=False)
  cpf_cnpj = StringField(required=False)
  code_country = StringField(required=False)
  phone = StringField(required=False)
  org_name = StringField(required=False)
  chatbot_user_id = StringField(required=False)
  picture = StringField(required=False)
  active = BooleanField(default=False)
  actived_at = DateTimeField(required=False)
  deactived_at = DateTimeField(required=False)

  class Config:
    json_encoders = {
        ObjectId: str
    }
    populate_by_name=True,
    orm_mode = True
    arbitrary_types_allowed = True
    allow_population_by_field_name = True
