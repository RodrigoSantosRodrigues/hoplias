import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING
from ...domain.model.specie_model import SpecieModel

class SpecieRepository:
    def __init__(self, db: AsyncIOMotorCollection):
        self.db = db
        self.collection = db['species']

    async def create(self, data):
        specie_data = SpecieModel(
            name=data.name,
            slug_name=data.slug_name,
            scientific_name=data.scientific_name,
            family=data.family,
            description=data.description,
            habitat=data.habitat,
            endangered=data.endangered,
            conservation_status=data.conservation_status,
            common_names=data.common_names,
            external_id=data.external_id,
            location_id=data.location_id,
            user_id=data.user_id,
            team_id=data.team_id,
            created_by_user=data.created_by_user,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(specie_data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: str, data: dict):
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

    async def get_by_name(self, name: str, team_id: str = None, user_id: str = None):
        query = {"name": name}

        if team_id:
            query['team_id'] = team_id
        if user_id:
            query['user_id'] = user_id

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
            query['slug_name'] = slug
        if search:
            query['$or'] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"scientific_name": {"$regex": search, "$options": "i"}}
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

        data_list = []
        async for specie in cursor:
            data_list.append({**specie, "id": str(specie["_id"])})

        return {
            "total": total_folders,
            "page": page,
            "page_size": page_size,
            "species": data_list
        }
