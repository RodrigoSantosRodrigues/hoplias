from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.model.user_recover_model import UserRecoverModel


class UserRecoverRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Class constructor
        """
        self.db = db
        self.collection = db['user_recovers']

    async def create(self, data):
        user_recover_data = UserRecoverModel(
            user_id=data.user_id,
            old_password=data.old_password,
            code=data.code,
            expiration_in_days=data.expiration_in_days,
            expiration_date=data.expiration_date,
            message_id=data.message_id,
            validated=data.validated,
            actived_at=data.actived_at,
            created_by_user=data.created_by_user,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(user_recover_data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return await self.get_by_id(str(model["_id"]))

    async def get_by_id(self, id: str):
        return await self.collection.find_one({"_id": id})

    async def get_code(self, code: str):
        return await self.collection.find_one({
            "code": code,
            "actived_at": None,
            "expiration_date": {"$gte": datetime.utcnow()}
        })

    async def get_valid_code(self, code: str):
        return await self.collection.find_one({
            "code": code,
            "validated": True,
            "actived_at": None,
            "expiration_date": {"$gte": datetime.utcnow()}
        })

    async def get_latest_recovery(self, user_id: int, team_id: int):
        return await self.collection.find_one({
            "user_id": user_id,
            "team_id": team_id
        }, sort=[("modified_at", -1)])

    async def get_pending_validations(self, user_id: int):
        return await self.collection.find_one({
            "user_id": user_id,
            "validated": False,
            "expiration_date": {"$gte": datetime.utcnow()}
        }, sort=[("modified_at", -1)])
