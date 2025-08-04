import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING
from ...domain.model.address_model import AddressModel

class AddressRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db['addresses']

    async def create(self, data):
        model = AddressModel(
            name=data.name,
            zip_code=data.zip_code,
            street=data.street,
            number=data.number,
            neighborhood=data.neighborhood,
            state=data.state,
            city=data.city,
            complement=data.complement,
            latitude=data.latitude,
            longitude=data.longitude,
            team_id=data.team_id,
            user_id=data.user_id,
            specie_id=data.specie_id,
            ideogram_id=data.ideogram_id,
            folder_id=data.folder_id,
            created_by_user=data.created_by_user,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()
        
        result = await self.collection.insert_one(model)
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
    
    async def get_by_name(self, name: str, team_id: str = None, user_id: str = None):
        query = {"name": name}

        if team_id:
            query['team_id'] = team_id
        if user_id:
            query['user_id'] = user_id

        return await self.collection.find_one(query)

    async def get_by_specie(self, specie_id: str, team_id: Optional[str] = None, user_id: Optional[str] = None):
        query = {"specie_id": specie_id}
        if team_id:
            query["team_id"] = team_id
        if user_id:
            query["user_id"] = user_id

        cursor = self.collection.find(query)
        return [address async for address in cursor]

    async def get_first_by_specie(self, specie_id: str, team_id: Optional[str] = None, user_id: Optional[str] = None):
        query = {"specie_id": specie_id}
        if team_id:
            query["team_id"] = team_id
        if user_id:
            query["user_id"] = user_id

        return await self.collection.find_one(query)

    async def get_by_search(self, search: str, team_id: Optional[str] = None, user_id: Optional[str] = None):
        query = {"$or": [
            {"name": {"$regex": search, "$options": "i"}},
            {"street": {"$regex": search, "$options": "i"}},
            {"neighborhood": {"$regex": search, "$options": "i"}},
            {"complement": {"$regex": search, "$options": "i"}},
            {"latitude": {"$regex": search, "$options": "i"}},
            {"longitude": {"$regex": search, "$options": "i"}}
        ]}
        
        if team_id:
            query["team_id"] = team_id
        if user_id:
            query["user_id"] = user_id

        cursor = self.collection.find(query).sort("modified_at", -1)
        data_list = []
        async for data in cursor:
            data_list.append({**data, "id": str(data["_id"])})
        return data_list

    async def get_all_by_team_or_user(
        self,
        order_by: str = "-created_at",
        search: str = "",
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
     
        if search:
            query = {"$or": [
                {"name": {"$regex": search, "$options": "i"}},
                {"street": {"$regex": search, "$options": "i"}},
                {"neighborhood": {"$regex": search, "$options": "i"}},
                {"complement": {"$regex": search, "$options": "i"}},
                {"latitude": {"$regex": search, "$options": "i"}},
                {"longitude": {"$regex": search, "$options": "i"}}
            ]}
 
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
        async for data in cursor:
            data_list.append({**data, "id": str(data["_id"])})

        return {
            "total": total_folders,
            "page": page,
            "page_size": page_size,
            "addresses": data_list
        }
