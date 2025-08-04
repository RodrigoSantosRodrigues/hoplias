import datetime
from pydantic import BaseModel


class TagDto(BaseModel):
  name: str
  description: str
 