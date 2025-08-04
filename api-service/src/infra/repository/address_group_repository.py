import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.model.address_group_model import AddressGroupModel

class AddressGroupRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db['addresses']

    async def create(self, data) -> AddressGroupModel:
        model = AddressGroupModel(
            team_id=data.team_id,
            user_id=data.user_id,
            address_id=data.address_id,
            specie_id=data.specie_id,
            ideogram_id=data.ideogram_id,
            folder_id=data.folder_id,
            kariotype_id=data.kariotype_id,
            created_by_user=data.created_by_user
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

    async def delete(self, model: dict):
        await self.collection.delete_one({"_id": model["_id"]})

    async def is_unique_combination(self, data):
        query = {
            "address_id": data.address_id,
            "specie_id": data.specie_id,
            "team_id": data.team_id,
            "user_id": data.user_id,
            "ideogram_id": data.ideogram_id,
            "folder_id": data.folder_id,
            "kariotype_id": data.kariotype_id
        }
        existing_doc = await self.collection.find_one(query)
        return existing_doc is None

    async def get_by_id(self, id: str) -> Optional[AddressGroupModel]:
        return await self.collection.find_one(
            {"_id": id}
        )

    async def get_by_specie(self, specie_id: str, team_id: Optional[str] = None, user_id: Optional[str] = None) -> List[AddressGroupModel]:
        query = {"specie_id": specie_id}
        if team_id:
            query["team_id"] = team_id
        if user_id:
            query["user_id"] = user_id

        cursor = self.collection.find(query).sort("modified_at", -1)
        return await cursor.to_list()

    async def get_by_ideogram(self, ideogram_id: str, team_id: Optional[str] = None, user_id: Optional[str] = None) -> List[AddressGroupModel]:
        query = {"ideogram_id": ideogram_id}
        if team_id:
            query["team_id"] = team_id
        if user_id:
            query["user_id"] = user_id

        cursor = self.collection.find(query).sort("modified_at", -1)
        return await cursor.to_list()

    async def get_all_by_team(self, team_id: str) -> List[AddressGroupModel]:
        cursor = self.collection.find(
            {"team_id": team_id}
        ).sort("modified_at", -1)
        return await cursor.to_list()
