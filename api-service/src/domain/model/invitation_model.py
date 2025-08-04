from mongoengine import fields
from .base_model import BaseModel

class InvitationModel(BaseModel):
  meta = {
    'collection': 'invitations'
  }
  
  actived = fields.BooleanField(default=False)
  revoked = fields.BooleanField(default=False)
  owner_user_id = fields.StringField(required=True)
  guest_user_id = fields.StringField(required=True)
  email = fields.StringField(required=True)
  team_id = fields.StringField(null=True)
  address_id = fields.StringField(null=True)
  specie_id = fields.StringField(null=True)
  ideogram_id = fields.StringField(null=True)
  folder_id = fields.StringField(null=True)
  kariotype_id = fields.StringField(null=True)
  send_mail = fields.BooleanField(default=False)
