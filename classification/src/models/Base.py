import datetime
from mongoengine import Document, fields
from bson import ObjectId

class BaseModel(Document):
  meta = {'abstract': True}

  id = fields.StringField(primary_key=True, alias="_id", default=lambda: str(ObjectId()))
  deleted_at = fields.DateTimeField(null=True)
  created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
  modified_at = fields.DateTimeField(default=datetime.datetime.utcnow)
  created_by_user = fields.StringField(null=True)
  modified_by_user = fields.StringField(null=True)
  deleted_by_user = fields.StringField(null=True)
