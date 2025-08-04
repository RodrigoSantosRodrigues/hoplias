from mongoengine import Document, fields
from .base_model import BaseModel

class IdeogramModel(BaseModel):
  meta = {
    'collection': 'ideograms'
  }

  name = fields.StringField(max_length=100, required=True)
  description = fields.StringField(max_length=300, required=False)
  citogenetic_view = fields.DictField(required=False)
  citogenomic_view = fields.DictField(required=False)
  text_gff = fields.StringField(required=False)
  kariotype_id = fields.StringField(required=False)
  folder_id = fields.StringField(required=False)
  address_id = fields.StringField(required=False)
  specie_id = fields.StringField(required=False)
  categories = fields.ListField(fields.StringField(), required=False)
  user_id = fields.StringField(required=True)
  team_id = fields.StringField(required=True)
