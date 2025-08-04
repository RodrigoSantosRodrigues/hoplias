from mongoengine import StringField, BooleanField, DateTimeField
from datetime import datetime
from .base_model import BaseModel

class TeamModel(BaseModel):
  meta = {
    'collection': 'teams'
  }

  name = StringField(required=True)
  description = StringField(required=False)
  user_id = StringField(required=True)
  active = BooleanField(default=True)
  actived_at = DateTimeField(default=datetime.utcnow)
  deactived_at = DateTimeField(required=False)
