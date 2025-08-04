from mongoengine import fields
from .base_model import BaseModel

class GrantModel(BaseModel):
  meta = {
    'collection': 'grants'
  }

  actived = fields.BooleanField(default=False)
  revoked = fields.BooleanField(default=False)
  invitation_id = fields.StringField(required=True)
  owner_user_id = fields.StringField(required=True)
  guest_user_id = fields.StringField(required=True)
  team_id = fields.StringField(required=True)
  roles = fields.ListField(fields.StringField(), default=[])
  rules = fields.ListField(fields.StringField(), default=[])
