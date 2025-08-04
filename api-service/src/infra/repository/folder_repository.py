import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING
from ...domain.model.folder_model import FolderModel


class FolderRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Class constructor
        :param db: Database connection
        """
        self.db = db
        self.collection = db['folders']

    async def create(self, data):
        folder_data = FolderModel(
            name=data.name,
            description=data.description,
            slug=data.slug,
            folder_parent_id=data.folder_parent_id,
            address_id=data.address_id,
            categories=data.categories,
            user_id=data.user_id,
            team_id=data.team_id,
            created_by_user=data.created_by_user,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(folder_data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.datetime.utcnow()

        await self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return await self.get_by_id(str(model["_id"]))

    async def delete(self, id: str):
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    async def get_by_id(self, id: str):
        return await self.collection.find_one({"_id": id})

    async def get_by_name_user_or_team(self, slug: str, team_id: str = None, user_id: str = None):
        query = {}
        if user_id:
            query['user_id'] = user_id
        if team_id:
            query['team_id'] = team_id
        query['slug'] = {"$regex": slug, "$options": "i"}

        return await self.collection.find_one(query)

    async def get_by_user_or_team(
        self,
        order_by: str = "-created_at",
        search: str = "",
        slug: str = None,
        team_id: str = None,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10
    ):
        query = {}
        if user_id:
            query['user_id'] = user_id
        if team_id:
            query['team_id'] = team_id
 
        if slug:
            query['slug'] = slug
        if search:
            query['$or'] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
 
        total_folders = await self.collection.count_documents(query)
  
        if order_by is None:
            order_by = "-created_at"

        sort_order = DESCENDING if order_by.startswith("-") else 1
        sort_field = order_by.lstrip("-")

        cursor = self.collection.find(query)\
                                .sort(sort_field, sort_order)\
                                .skip((page - 1) * page_size)\
                                .limit(page_size)

        folder_list = []
        async for folder in cursor:
            folder_list.append({**folder, "id": str(folder["_id"])})

        return {
            "total": total_folders,
            "page": page,
            "page_size": page_size,
            "folders": folder_list
        }
