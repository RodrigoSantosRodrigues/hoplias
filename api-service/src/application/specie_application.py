from typing import Any
from io import BytesIO
from fastapi import Request, UploadFile
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict, Any

from ..domain.interfaces.request.specie_request import CreateSpecie, UpdateSpecie
from ..domain.interfaces.request.address_request import CreateAddress, CreateAddressGroup
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.enums.specie_enum import ImportFieldsEnum
from ..infra.repository.specie_repository import SpecieRepository
from ..infra.repository.user_repository import UserRepository
from ..infra.repository.address_repository import AddressRepository
from ..infra.repository.address_group_repository import AddressGroupRepository
from ..domain.enums.rules_enum import RolesEnum
from ..helpers.utils import slugify
from ..infra.config import logger


async def create_specie(
  data: CreateSpecie,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  specie_repository = SpecieRepository(db)

  if await specie_repository.get_by_name(
    name=data.name,
    user_id=auth if not data.team_id else None,
    team_id=data.team_id if data.team_id else None
  ):
    return {
      'error': True,
      'message': MessagesEnum.ALREAD_EXISTS
    }

  data.team_id = data.team_id if data.team_id else None
  data.user_id = auth if not data.team_id else None
  data.created_by_user = auth
  data.slug_name = slugify(data.name)
  specie = await specie_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'data': {**specie, "id": str(specie.get('_id'))}
  }


async def get_by_search(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str,
  order_by: str,
  search: str,
  page: int = 1,
  page_size: int = 10
) -> Any:
  specie_repository = SpecieRepository(db)

  species = await specie_repository.get_by_user_or_team(
    order_by=order_by,
    search=search,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
    page=page,
    page_size=page_size
  )

  return species


async def get_specie(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Any:
  specie_repository = SpecieRepository(db)
  user_repository = UserRepository(db)

  user = await user_repository.get_by_id(auth)
  if not user:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND_USER
    }

  specie = await specie_repository.get_by_id(id)
  if not specie:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  return {
    'success': True,
    'message': MessagesEnum.SUCCESS,
    'data': {**specie, "id": str(specie.get('_id'))}
  }


async def update_specie(
  id: str,
  data: UpdateSpecie,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Any:
  specie_repository = SpecieRepository(db)
  
  specie = await specie_repository.get_by_id(id)
  if not specie:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  data.modified_by_user = auth
  data.user_id = specie.get('user_id')
  data.team_id = specie.get('team_id')

  update_data = data.dict(exclude_unset=True)
  specie_updated = await specie_repository.update(specie, update_data)

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': specie_updated
  }


async def remove_specie(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str
) -> Dict[str, str]:
  specie_repository = SpecieRepository(db)

  specie = await specie_repository.get_by_id(id)
  if not specie:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await specie_repository.delete(specie)

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
