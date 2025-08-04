from mongoengine import StringField, BooleanField, DateTimeField, IntField
from datetime import datetime
from .base_model import BaseModel

class CategoryModel(BaseModel):
  meta = {
      'collection': 'categories'
  }

  name = StringField(required=True)
  slug = StringField(required=False)
  description = StringField(required=False)
  active = BooleanField(required=True, default=True)
  actived_at = DateTimeField(default=datetime.utcnow)
  deactived_at = DateTimeField(required=False)
  team_id = StringField(required=False, default=False)
  user_id = StringField(required=False, default=False)
