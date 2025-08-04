from mongoengine import StringField, BooleanField, IntField, ListField
from datetime import datetime
from .base_model import BaseModel

class SpecieModel(BaseModel):
  meta = {
    'collection': 'species'
  }

  name = StringField(required=True)
  slug_name = StringField(required=True)
  scientific_name = StringField(required=True, max_length=200)
  family = StringField(required=True, max_length=100)
  description = StringField(required=False, max_length=900)
  habitat = StringField(required=False, max_length=200)
  endangered = BooleanField(default=False)
  conservation_status = StringField(required=False, max_length=100)
  common_names = ListField(StringField(), required=False)  
  external_id = StringField(required=False)
  location_id = StringField(required=False)
  user_id = StringField(required=True)
  team_id = StringField(required=True)
