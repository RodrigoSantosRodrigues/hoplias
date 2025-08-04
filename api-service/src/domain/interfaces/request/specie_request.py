from pydantic import BaseModel
from ..dto.specie_dto import SpecieDto, UpdateDto


class Login(BaseModel):
  email: str = None
  password: str = None


class CreateSpecie(SpecieDto):
  pass

class UpdateSpecie(UpdateDto):
  pass
