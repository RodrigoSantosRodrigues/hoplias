from typing import Any
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict, Any

from ..domain.interfaces.request.address_request import (
  CreateAddress,
  CreateAddressGroup,
  UpdateDto
)
from ..infra.repository.address_repository import AddressRepository
from ..infra.repository.address_group_repository import AddressGroupRepository
from ..domain.enums.messages_enum import MessagesEnum


async def create_address(
  data: CreateAddress,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict:
  address_repository = AddressRepository(db)

  address = await address_repository.get_by_name(
    name=data.name,
    team_id=data.team_id if data.team_id else None,
    user_id=auth if not data.team_id else None,
  )

  if address:
    return {
      'success': False,
      'message': MessagesEnum.ALREAD_EXISTS
    }

  data.user_id = auth if not data.team_id else None
  data.team_id = data.team_id if data.team_id else None
  data.created_by_user = auth
  address = await address_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'data': {**address, "id": str(address.get('_id'))}
  }


async def create_address_group(
  data: CreateAddressGroup,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Any:
  address_repository = AddressRepository(db)
  address_group_repository = AddressGroupRepository(db)

  address = await address_repository.get_by_id(data.address_id)
  if not address:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  data.user_id = auth if not data.team_id else None
  data.team_id = data.team_id if data.team_id else None
  data.created_by_user = auth

  if not await address_group_repository.is_unique_combination(data):
    return {
      'success': False,
      'message': MessagesEnum.ALREAD_EXISTS
    }

  await address_group_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED
  }


async def get_address_by_id(
  address_id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Any:
  address_repository = AddressRepository(db)

  addreses = await address_repository.get_by_id(address_id)
  return {
    'success': True,
    'message': MessagesEnum.SUCCESS,
    'data': {**addreses, "id": str(addreses.get('_id'))}
  }


async def get_by_search(
  search: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str = None
) -> Any:
  address_repository = AddressRepository(db)
  
  addreses = await address_repository.get_by_search(
    search=search,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
  )
  return addreses


async def get_address_by_specie(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  specie_id: str,
  team_id: str = None
) -> Any:
  address_repository = AddressRepository(db)

  addreses = await address_repository.get_by_specie(
    specie_id,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
  )

  return addreses


async def get_address_by_team_or_user(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str,
  order_by: str,
  search: str,
  page: int = 1,
  page_size: int = 10
) -> Any:
  address_repository = AddressRepository(db)

  addresses = await address_repository.get_all_by_team_or_user(
    order_by=order_by,
    search=search,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
    page=page,
    page_size=page_size
  )

  return addresses


async def update_address(
  id: str,
  data: UpdateDto,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict:
  address_repository = AddressRepository(db)

  address = await address_repository.get_by_id(id)
  if not address:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  data.modified_by_user = auth
  data.user_id = address.get('user_id')
  data.team_id = address.get('team_id')
  
  update_data = data.dict(exclude_unset=True)

  address = await address_repository.update(address, update_data)

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': address
  }


async def remove_address(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict[str, str]:
  address_repository = AddressRepository(db)

  address = await address_repository.get_by_id(id)
  if not address:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await address_repository.delete(address)

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
