from bson import ObjectId
from mongoengine import  StringField, FloatField, DateTimeField, IntField, ListField
from datetime import datetime
from .base_model import BaseModel

class FolderModel(BaseModel):
  meta = {
    'collection': 'folders'
  }

  name = StringField(required=True)
  slug = StringField(required=False)
  description = StringField(required=False)
  folder_parent_id = StringField(required=False)
  address_id = StringField(required=False)
  categories = ListField(StringField(), required=False)
  user_id = StringField(required=False)
  team_id = StringField(required=False)

  class Config:
    json_encoders = {
        ObjectId: str
    }
    populate_by_name=True,
    orm_mode = True
    arbitrary_types_allowed = True
    allow_population_by_field_name = True
