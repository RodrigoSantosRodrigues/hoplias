from pydantic import BaseModel, EmailStr
from typing import Union
from ..dto.user_dto import UserDto


class Login(BaseModel):
  email: Union[str, None] = None
  password: Union[str, None] = None

class AccessChatbot(BaseModel):
  email: Union[str, None] = None
  name: Union[str, None] = None
  chatbot_user_id: Union[str, None] = None

class CreateUser(UserDto):
  invite_id: Union[str, None] = None
  picture: Union[str, None] = None
  
  def setPassword(self, value):
    self.password = value

  def setNotActive(self, value):
    self.active = value


class CreateUserGoogle(BaseModel):
  token: str
  invite_id: Union[str, None] = None


class UpdateUser(UserDto):
  def setPassword(self, value):
    self.password = value

class RecoverPasswordUser(BaseModel):
  email: EmailStr

class CodeValidationUser(BaseModel):
  code: str

class UpdatePasswordUser(BaseModel):
  code: str
  password: str

  def setPassword(self, value):
    self.password = value
