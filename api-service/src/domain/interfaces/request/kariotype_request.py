from pydantic import BaseModel
from ..dto.kariotype_dto import KariotypeDto, UpdateDto


class CreateKariotype(BaseModel):
  chromosomes: dict
  properties: KariotypeDto

class CreateKariotypeRequest(KariotypeDto):
  pass

class UpdateKariotype(UpdateDto):
  pass
