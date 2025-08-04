from mongoengine import fields
from .base_model import BaseModel

class ShareModel(BaseModel):
  meta = {
    'collection': 'shareds'
  }

  actived = fields.BooleanField(default=False)
  revoked = fields.BooleanField(default=False)
  invitation_id = fields.StringField(required=True)
  owner_user_id = fields.StringField(required=True)
  guest_user_id = fields.StringField(required=True)
  address_id = fields.StringField(null=True)
  specie_id = fields.StringField(null=True)
  ideogram_id = fields.StringField(null=True)
  folder_id = fields.StringField(null=True)
  kariotype_id = fields.StringField(null=True)
  roles = fields.ListField(fields.StringField(), default=[])
  rules = fields.ListField(fields.StringField(), default=[])
