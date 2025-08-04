from typing import Any
from fastapi import Request, Depends
from itertools import zip_longest
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Any, Dict

from ..domain.interfaces.request.folder_request import CreateFolderDto, UpdateFolderDto
from ..infra.repository.folder_repository import FolderRepository
from ..infra.repository.category_repository import CategoryRepository
from ..domain.enums.messages_enum import MessagesEnum
from ..domain.interfaces.dto.category_dto import CategoryData
from ..helpers.utils import slugify


async def create_folder(
  data: CreateFolderDto,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
) -> Dict:
  folder_repository = FolderRepository(db)
  category_repository = CategoryRepository(db)

  folder = await folder_repository.get_by_name_user_or_team(slugify(data.name), data.team_id, auth)
  if folder:
    return {
      'success': False,
      'message': MessagesEnum.ALREAD_EXISTS
    }

  for category in data.categories_name:
    category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
    if category_slug:
      data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
    else:
      await category_repository.create(
        CategoryData(
          name=category,
          slug=slugify(category),
          description='',
          team_id=data.team_id if data.team_id else None,
          user_id=auth if not data.team_id else None
        ))
      category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
      if category_slug:
        data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None

  del data.categories_name
  data.slug=slugify(data.name)
  data.user_id = auth if not data.team_id else None
  data.team_id = data.team_id if data.team_id else None
  data.created_by_user = auth

  await folder_repository.create(data)

  return {
    'success': True,
    'message': MessagesEnum.CREATED,
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
  folder_repository = FolderRepository(db)

  folders = await folder_repository.get_by_user_or_team(
    order_by=order_by,
    search=search,
    team_id=team_id if team_id else None,
    user_id=auth if not team_id else None,
    page=page,
    page_size=page_size
  )

  return folders


async def get_folder_by_id(
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  id: str
) -> Any:
  folder_repository = FolderRepository(db)

  folder = await folder_repository.get_by_id(id)
  if not folder:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  return {
      'success': True,
      'message': MessagesEnum.SUCCESS,
      'data': {**folder, "id": str(folder.get('_id'))}
    }


async def update_folder(
  id: str,
  data: UpdateFolderDto,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str = None
) -> Any:
  folder_repository = FolderRepository(db)
  category_repository = CategoryRepository(db)

  data.modified_by_user = auth

  for category in data.categories_name:
    category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
    if category_slug:
      data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
    else:
      await category_repository.create(
        CategoryData(
          name=category,
          slug=slugify(category),
          description='',
          team_id=data.team_id if data.team_id else None,
          user_id=auth if not data.team_id else None
        ))
      category_slug = await category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, auth)
      if category_slug:
        data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None

  folder = await folder_repository.get_by_id(id)
  if not folder:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  folder_updated = await folder_repository.update(folder, {
    'name': data.name,
    'description': data.description,
    'categories': list(set([a + b for a, b in zip_longest(folder.get('categories'), data.categories, fillvalue=0)])),
    'modified_by_user': auth
  })

  return {
    'success': True,
    'message': MessagesEnum.UPDATED,
    'data': {**folder_updated, "id": str(folder_updated.get('_id'))}
  }


async def remove_folder(
  id: str,
  request: Request,
  db: AsyncIOMotorCollection,
  auth: str,
  team_id: str = None
) -> Dict[str, str]:
  folder_repository = FolderRepository(db)

  folder = await folder_repository.get_by_id(id)
  if not folder:
    return {
      'success': False,
      'message': MessagesEnum.NOT_FOUND
    }

  await folder_repository.delete(folder)

  return {
    'success': True,
    'message': MessagesEnum.DELETED
  }
