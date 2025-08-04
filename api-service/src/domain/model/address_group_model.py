from mongoengine import fields
from .base_model import BaseModel

class AddressGroupModel(BaseModel):
  meta = {
    'collection': 'address_groups'
  }

  team_id = fields.StringField(null=True)
  user_id = fields.StringField(null=True)
  address_id = fields.StringField(required=True)
  specie_id = fields.StringField(null=True)
  ideogram_id = fields.StringField(null=True)
  folder_id = fields.StringField(null=True)
  kariotype_id = fields.StringField(null=True)
