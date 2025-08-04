from mongoengine import fields
from .base_model import BaseModel

class VisualizationModel(BaseModel):
    meta = {
        'collection': 'visualizations',
        'indexes': [
            {'fields': ['address_id', 'specie_id', 'ideogram_id', 'kariotype_id'], 'unique': True}
        ]
    }

    address_id = fields.StringField(null=True)
    specie_id = fields.StringField(null=True)
    ideogram_id = fields.StringField(null=True)
    kariotype_id = fields.StringField(null=True)
    view_value = fields.IntField(required=True, default=0)
    users_viewed = fields.ListField(fields.StringField(), default=[])
    unique_users_viewed = fields.IntField(default=0)
