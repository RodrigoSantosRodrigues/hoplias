import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING
from ...domain.model.ideogram_model import IdeogramModel


class IdeogramRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db['ideograms']

    async def create(self, data):
        ideogram_data = IdeogramModel(
            name=data.name,
            description=data.description,
            citogenetic_view=data.citogenetic_view,
            citogenomic_view=data.citogenomic_view,
            text_gff=data.text_gff,
            kariotype_id=data.kariotype_id,
            folder_id=data.folder_id,
            address_id=data.address_id,
            specie_id=data.specie_id,
            categories=data.categories,
            user_id=data.user_id,
            team_id=data.team_id,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(ideogram_data)
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
        query = {"_id": id}
        return await self.collection.find_one(query)

    async def get_by_kariotype_id(self, kariotype_id: str):
        query = {"kariotype_id": kariotype_id}
        return await self.collection.find_one(query)

    async def get_by_user_or_team(
        self,
        start_date: str, 
        end_date: str,
        order_by: str = "-created_at",
        search: str = "",
        team_id: str = None,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10,
    ):
        query = {}
        if user_id:
            query['user_id'] = user_id
        if team_id:
            query['team_id'] = team_id
        
        if start_date and end_date:
            start_dt = datetime.datetime.strptime(start_date.split(' ')[0], '%Y-%m-%d')
            end_dt = datetime.datetime.strptime(end_date.split(' ')[0], '%Y-%m-%d')
            query["created_at"] = {"$gte": start_dt, "$lte": end_dt}

        if search:
            query['$or'] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]

        total_ideograms = await self.collection.count_documents(query)

        if order_by is None:
            order_by = "-created_at"

        sort_order = DESCENDING if order_by.startswith("-") else 1
        sort_field = order_by.lstrip("-")

        cursor = self.collection.find(query)\
                                .sort(sort_field, sort_order)\
                                .skip((page - 1) * page_size)\
                                .limit(page_size)

        ideogram_list = []
        async for ideogram in cursor:
            ideogram_list.append({**ideogram, "id": str(ideogram["_id"])})

        return {
            "total": total_ideograms,
            "page": page,
            "page_size": page_size,
            "items": ideogram_list
        }
