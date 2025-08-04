from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING
from ...domain.model.team_model import TeamModel
from ...domain.enums.rules_enum import RolesEnum, RulesEnum

class TeamRepository:
    def __init__(self, db: AsyncIOMotorCollection):
        self.db = db
        self.collection = db['teams']
        self.collection_grants = db['grants']

    async def create(self, data):
        team_data = TeamModel(
            name=data.name,
            description=data.description,
            user_id=data.user_id,
            active=data.active,
            actived_at=datetime.utcnow(),
            created_by_user=data.created_by_user,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(team_data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: str, data: dict):
        update_data = {key: value for key, value in data.items() if value is not None}
        update_data['modified_at'] = datetime.utcnow()

        await self.collection.update_one({"_id": model["_id"]}, {"$set": update_data})
        return await self.get_by_id(model["_id"])

    async def delete(self, id: str):
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    async def get_by_id(self, id: str):
        return await self.collection.find_one({"_id": id})
    
    async def get_by_name(self, name: str, user_id: str = None):
        query = {
            "$or": [
                {"name": name}
            ]
        }
        query['user_id'] = user_id
        return await self.collection.find_one(query)

    async def get_by_user(
        self,
        order_by: str = "-created_at",
        search: str = "",
        user_id: str = None,
        page: int = 1,
        page_size: int = 10
    ):
        query = {}
        query['$or'] = [
            {"user_id": user_id},
            {"guest_user_id": user_id, "actived": True, "revoked": False}
        ]

        if search:
            query['$and'] = [
                {"$or": [
                    {"user_id": user_id},
                    {"guest_user_id": user_id, "actived": True, "revoked": False}
                ]},
                {"$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}
                ]}
            ]

        grants_by_team_id = {}
        accessible_team_ids = []

        grants_cursor = self.collection_grants.find({
            "guest_user_id": user_id,
            "revoked": False,
            "actived": True
        })

        async for grant in grants_cursor:
            team_id = grant["team_id"]
            accessible_team_ids.append(team_id)
            grants_by_team_id[team_id] = {
                "roles": grant.get("roles"),
                "rules": grant.get("rules")
            }

        if accessible_team_ids:
            query["$or"].append(
                {"_id": {"$in": accessible_team_ids}}
            )

        total = await self.collection.count_documents(query)

        if order_by is None:
            order_by = "-created_at"

        sort_order = DESCENDING if order_by.startswith("-") else 1
        sort_field = order_by.lstrip("-")

        cursor = self.collection.find(query)\
                                .sort(sort_field, sort_order)\
                                .skip((page - 1) * page_size)\
                                .limit(page_size)

        list_ = []
        async for team in cursor:
            team_data = {**team, "id": str(team["_id"])}

            if team["_id"] in grants_by_team_id:
                team_data.update(grants_by_team_id[team["_id"]])
            else:
                team_data.update({
                    "roles": [role.value for role in RolesEnum],
                    "rules": [rule.value for rule in RulesEnum]
                })
            list_.append(team_data)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "teams": list_
        }
