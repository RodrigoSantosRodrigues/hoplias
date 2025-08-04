from typing import Any
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any

from ..domain.interfaces.request.ideogram_request import CreateIdeogramDto, UpdateIdeogramDto
from ..infra.repository.ideogram_repository import IdeogramRepository
from ..infra.repository.category_repository import CategoryRepository
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.interfaces.dto.category_dto import CategoryData
from ..helpers.utils import slugify


async def create_ideogram(
  data: CreateIdeogramDto,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int,
) -> Dict:
  ideogram_repository = IdeogramRepository(db)
  category_repository = CategoryRepository(db)

  for category in data.categories_name:
    category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
    if category_slug:
      data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
    else:
      await category_repository.create(
        CategoryData(
          name= category,
          slug= slugify(category),
          description= '',
          team_id= data.team_id,
          user_id=auth
        ))
      category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
      if category_slug:
        data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None

  del data.categories_name
  data.user_id = auth
  data.team_id = data.team_id
  data.created_by_user = auth

  ideogram = await ideogram_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
    'data': {**ideogram, "id": str(ideogram.get('_id'))}
  }


async def get_ideogram_by_id(
  id: int,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int
) -> Any:
  ideogram_repository = IdeogramRepository(db)

  ideogram = await ideogram_repository.get_by_id(id)
  return {
    'success': True,
    'message': MessagesEnum.SUCCESS,
    'data': {**ideogram, "id": str(ideogram.get('_id'))}
  }


async def get_all_ideogram(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int,
  team_id: str,
  order_by: str = None,
  search: str = None,
  page: int = 1,
  page_size: int = 10,
  start_date: str = None,
  end_date: str = None
) -> Any:
  ideogram_repository = IdeogramRepository(db)

  ideograms = await ideogram_repository.get_by_user_or_team(
    start_date=start_date,
    end_date=end_date,
    order_by=order_by,
    search=search,
    team_id=team_id,
    user_id=auth,
    page=page,
    page_size=page_size
  )

  return ideograms


async def update_ideogram(
  id: int,
  data: UpdateIdeogramDto,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int
) -> Any:
  ideogram_repository = IdeogramRepository(db)

  data.modified_by_user = auth
  update_data = data.dict(exclude_unset=True)

  ideogram = await ideogram_repository.get_by_id(id)
  if not ideogram:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  ideogram_updated = await ideogram_repository.update(ideogram, update_data)

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': ideogram_updated
  }


async def remove_ideogram(
  id: int,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: int
) -> Dict[str, str]:
  ideogram_repository = IdeogramRepository(db)

  ideogram = await ideogram_repository.get_by_id(id)
  if not ideogram:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await ideogram_repository.delete(ideogram.get('_id'))

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
