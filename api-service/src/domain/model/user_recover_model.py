import datetime
from mongoengine import fields
from .base_model import BaseModel

class UserRecoverModel(BaseModel):
  meta = {
    'collection': 'user_recovers'
  }

  user_id = fields.StringField(required=True)
  old_password = fields.StringField(max_length=128, null=True)
  code = fields.StringField(max_length=128, required=True)
  expiration_in_days = fields.IntField(null=True)
  expiration_date = fields.DateTimeField(null=True)
  message_id = fields.StringField(max_length=200, required=True)
  validated = fields.BooleanField(default=False, null=True)
  actived_at = fields.DateTimeField(null=True)
