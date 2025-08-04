from pydantic import BaseModel
from ..dto.address_dto import AddressDto, AddressGroupDto, UpdateDto


class CreateAddress(AddressDto):
  pass

class CreateAddressGroup(AddressGroupDto):
  pass

class UpdateAddress(UpdateDto):
  pass
