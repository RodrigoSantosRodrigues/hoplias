import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.model.share_model import ShareModel


class ShareRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Class constructor
        :param db: Database connection
        """
        self.db = db
        self.collection = db['shareds']

    async def create(self, data):
        share_data = ShareModel(
            invitation_id=data.invitation_id,
            owner_user_id=data.owner_user_id,
            guest_user_id=data.guest_user_id,
            address_id=data.address_id,
            specie_id=data.specie_id,
            ideogram_id=data.ideogram_id,
            folder_id=data.folder_id,
            kariotype_id=data.kariotype_id,
            roles=data.roles,
            rules=data.rules,
            actived=data.actived,
            revoked=data.revoked,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(share_data)
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

    async def get_by_id(self, share_id: str):
        query = {"_id": share_id}
        return await self.collection.find_one(query)

    async def get_by_owner_user_id(self, owner_user_id: str):
        query = {"owner_user_id": owner_user_id}
        return await self.collection.find(query).sort("modified_at", -1).to_list()

    async def get_active_shareds(self, owner_user_id: str = None):
        query = {"actived": True, "revoked": False}
        if owner_user_id:
            query["owner_user_id"] = owner_user_id
        return await self.collection.find(query).sort("modified_at", -1).to_list()

    async def get_by_search(self, search: str, owner_user_id: str = None, guest_user_id: str = None):
        query = {
            "$or": [
                {"guest_user_id": {"$regex": search, "$options": "i"}},
                {"guest_user_id": guest_user_id}
            ]
        }
        if owner_user_id:
            query["owner_user_id"] = owner_user_id
        return await self.collection.find(query).sort("modified_at", -1).to_list()

    async def get_all(self, owner_user_id: str):
        query = {"owner_user_id": owner_user_id}
        return await self.collection.find(query).sort("modified_at", -1).to_list()
