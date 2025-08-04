import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.model.grant_model import GrantModel


class GrantRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db['grants']

    async def create(self, data):
        grant_data = GrantModel(
            owner_user_id=data.owner_user_id,
            guest_user_id=data.guest_user_id,
            invitation_id=data.invitation_id,
            team_id=data.team_id,
            roles=data.roles,
            rules=data.rules,
            actived=data.actived,
            revoked=data.revoked,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(grant_data)
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

    async def get_by_id(self, grant_id: str):
        return await self.collection.find_one({"_id": grant_id})

    async def get_by_invitation_id(self, invitation_id: str):
        return await self.collection.find_one({"invitation_id": invitation_id})

    async def get_by_owner_user_id(self, owner_user_id: str):
        cursor = self.collection.find({"owner_user_id": owner_user_id}).sort("modified_at", -1)
        return [grant async for grant in cursor]

    async def get_active_grants(self, owner_user_id: str = None):
        query = {"actived": True, "revoked": False}
        if owner_user_id:
            query["owner_user_id"] = owner_user_id
        cursor = self.collection.find(query).sort("modified_at", -1)
        return [grant async for grant in cursor]

    async def get_by_search(self, search: str, owner_user_id: str = None, guest_user_id: str = None):
        query = {
            "$or": [
                {"guest_user_id": {"$regex": guest_user_id, "$options": "i"}},
                {"guest_user_id": {"$regex": search, "$options": "i"}}
            ]
        }
        if owner_user_id:
            query["owner_user_id"] = owner_user_id
        cursor = self.collection.find(query).sort("modified_at", -1)
        return [grant async for grant in cursor]

    async def get_all(self, owner_user_id: str):
        cursor = self.collection.find({"owner_user_id": owner_user_id}).sort("modified_at", -1)
        return [grant async for grant in cursor]
