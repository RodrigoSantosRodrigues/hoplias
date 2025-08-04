import datetime
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING
from ...domain.model.kariotype_model import KariotypeModel, Chromosome
from ...domain.enums.status_enum import StatusKariotypeEnum


class KariotypeRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db['kariotypes']

    async def create(self, data):
        kariotype_data = KariotypeModel(
            name=data.name,
            description=data.description,
            status=data.status,
            chromosome_number=data.chromosome_number,
            block_threshold=data.block_threshold,
            canva=data.canva,
            chromosomes = [chromosome.dict() for chromosome in data.chromosomes],
            segmented_automatic = [chromosome.dict() for chromosome in data.segmented_automatic],
            categories=data.categories,
            field_of_view=data.field_of_view,
            image_resolution=data.image_resolution,
            width = data.width,
            height = data.height,
            top = data.top,
            left = data.left,
            size = data.size,
            type_extension = data.type_extension,
            user_id=data.user_id,
            team_id=data.team_id,
            file_s3=data.file_s3,
            folder_s3=data.folder_s3,
            file_gcs=data.file_gcs,
            folder_gcs=data.folder_gcs,
            file_local=data.file_local,
            folder_local=data.folder_local,
            file_drive=data.file_drive,
            file_drive_id= data.file_drive_id,
            folder_drive=data.folder_drive,
            batches_total=data.batches_total,
            address_id=data.address_id,
            specie_type=data.specie_type,
            ordenation_type=data.ordenation_type,
            scheduled=data.scheduled or datetime.datetime.utcnow(),
            specie_id=data.specie_id,
            folder_id=data.folder_id,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(kariotype_data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.datetime.utcnow()

        await self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return await self.get_by_id(str(model["_id"]))

    async def bulk_update(self, parent_id: str, update_fields: List[dict]):
        """
        Updates specific chromosomes in a document based on the `id` and fields to update.

        :param parent_id: The ID of the parent document containing the chromosomes array.
        :param update_fields: List of dictionaries containing `id` of the chromosome and fields to update.
        :return: None
        """
        updated = None
        for update in update_fields:
            chromosome_id = update.get("id_chromosome", None)

            current_time = datetime.datetime.utcnow()
            update["modified_at"] = current_time 

            query = {}
            for key, value in update.items():
                query[f"chromosomes.$.{key}"] = value
        
            updated = await self.collection.update_one(
                {
                    "_id": parent_id,
                    "chromosomes.id_chromosome": chromosome_id
                },
                {
                    "$set": query
                },
                upsert=True
            )

        return updated

    async def delete(self, id: str):
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    async def get_by_id(self, id: str):
        query = {"_id": id}
        return await self.collection.find_one(query)

    async def get_by_user_or_team(
        self,
        order_by: str, 
        search: str, 
        start_date: str = None, 
        end_date: str = None,
        status: str = StatusKariotypeEnum.PENDING, 
        page: int = 1, 
        page_size: int = 10, 
        team_id: str = None, 
        user_id: str = None,
        by_today: bool = False
    ):
        query = {}
        if user_id:
            query['user_id'] = user_id
        if team_id:
            query['team_id'] = team_id
        
        if search:
            query['$or'] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]

        if by_today and bool(by_today):
            today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + datetime.timedelta(days=1)
            query['scheduled'] = {"$gte": today, "$lt": tomorrow}

        if (start_date and end_date) and (start_date != '' and end_date != ''):
            start_dt = datetime.datetime.strptime(start_date.split(' ')[0], '%Y-%m-%d')
            end_dt = datetime.datetime.strptime(end_date.split(' ')[0], '%Y-%m-%d')
            query["created_at"] = {"$gte": start_dt, "$lte": end_dt}

        if status:
            query["status"] = {"$regex": status, "$options": "i"}

        total_folders = await self.collection.count_documents(query)
  
        if order_by is None or order_by != '':
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
            "items": data_list
        }
