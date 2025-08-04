from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.model.user_model import UserModel


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Class constructor
        """
        self.db = db
        self.collection = db['users']

    async def create(self, data):
        data = UserModel(
            name=data.name,
            email=data.email,
            password=data.password,
            cpf_cnpj=data.cpf_cnpj,
            code_country=data.code_country,
            phone=data.phone,
            org_name=data.org_name,
            chatbot_user_id=data.chatbot_user_id,
            picture=data.picture,
            active=data.active,
            actived_at=data.actived_at,
            deactived_at=data.deactived_at,
            created_by_user=data.created_by_user,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return await self.get_by_id(str(model["_id"]))

    async def delete(self, user_id: str):
        result = await self.collection.delete_one({"_id": user_id})
        return result.deleted_count == 1

    async def get_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def get_by_id(self, user_id: str):
        return await self.collection.find_one({"_id": user_id})
    
    async def get_by_chatbot_user_id(self, chatbot_user_id: str):
        return await self.collection.find_one({"chatbot_user_id": chatbot_user_id})

    async def get_by_team_and_user_id(self, team_id: str, user_id: str):
        return await self.collection.find_one({"team_id": team_id, "_id": user_id})

    async def get_all_by_team(self, team_id: str, page: int = 1, page_size: int = 10):
        total_users = await self.collection.count_documents({"team_id": team_id})
        users_cursor = self.collection.find({"team_id": team_id}, {"password": 0})\
                                      .sort("modified_at", -1)\
                                      .skip((page - 1) * page_size)\
                                      .limit(page_size)

        users = await users_cursor.to_list(length=page_size)
        return {"total": total_users, "page": page, "page_size": page_size, "users": users}

    async def get_by_team(self, team_id: str, order_by: str, search: str, page: int = 1, page_size: int = 10):
        query = {
            "team_id": team_id,
            "$or": [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"cpf_cnpj": {"$regex": search, "$options": "i"}}
            ]
        }

        total_users = await self.collection.count_documents(query)

        users_cursor = self.collection.find(query, {"password": 0})\
                                      .sort(order_by, -1)\
                                      .skip((page - 1) * page_size)\
                                      .limit(page_size)

        users = await users_cursor.to_list(length=page_size)
        return {"total": total_users, "page": page, "page_size": page_size, "users": users}
