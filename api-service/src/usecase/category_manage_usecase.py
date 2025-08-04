from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict

from ..infra.repository.category_repository import CategoryRepository
from ..domain.interfaces.dto.category_dto import CategoryData
from ..domain.interfaces.request.kariotype_request import CreateKariotype
from ..helpers.utils import slugify


class CategoryManage:
  def __init__(
      self,
      request: Request,
      db: AsyncIOMotorCollection,
      auth: str,
    ):
    self.__request = request
    self.__db = db
    self.__auth = auth
    self.category_repository = CategoryRepository(self.__db)

  async def create_or_update_category(self, data) -> Dict:
    for category in data.categories_name:
        category_slug = await self.category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, self.auth)
        if category_slug:
            data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
        else:
            await self.category_repository.create(
                CategoryData(
                name= category,
                slug= slugify(category),
                description= '',
                team_id= data.team_id if data.team_id else None,
                user_id=self.__auth if not data.team_id else None
                ))
            category_slug = await self.category_repository.get_by_slug_and_team_or_user(slugify(category), data.team_id, self.auth)
            if category_slug:
                data.categories.append(category_slug.get('_id')) if category_slug.get('_id') not in data.categories else None
    del data.categories_name
    return data
