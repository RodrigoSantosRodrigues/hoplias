from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from ..dto.user_dto import UserDto

PyObjectId = Annotated[str, BeforeValidator(str)]

class ResponseUser(UserDto):
  id: PyObjectId = Field(alias="_id", default=None)

  class Config:
        populate_by_name=True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
