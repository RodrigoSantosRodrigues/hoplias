from mongoengine import fields
from .base_model import BaseModel

class AddressModel(BaseModel):
  meta = {
    'collection': 'addresses'
  }

  name = fields.StringField(max_length=300, required=True)
  zip_code = fields.StringField(max_length=50, required=True)
  street = fields.StringField(max_length=200, null=True)
  number = fields.IntField(null=True)
  neighborhood = fields.StringField(max_length=200, required=False)
  state = fields.StringField(max_length=100, required=False)
  city = fields.StringField(max_length=100, required=False)
  complement = fields.StringField(max_length=100, null=True)
  country = fields.StringField(max_length=100, null=True)
  latitude = fields.StringField(null=True)
  longitude = fields.StringField(null=True) 
  team_id = fields.StringField(required=False)
  user_id = fields.StringField(required=False)
  specie_id = fields.StringField(null=True)
  ideogram_id = fields.StringField(null=True)
  folder_id = fields.StringField(null=True)
  kariotype_id = fields.StringField(null=True)
