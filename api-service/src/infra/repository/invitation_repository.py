from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.model.invitation_model import InvitationModel
from pymongo import DESCENDING

from ...domain.enums.rules_enum import RolesEnum, RulesEnum


class InvitationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Class constructor
        :param db: Database connection
        """
        self.db = db
        self.collection = db['invitations']
        self.collection_grants = db['grants']

    async def create(self, data):
        invitation_data = InvitationModel(
            owner_user_id=data.owner_user_id,
            guest_user_id=data.guest_user_id,
            email=data.email,
            team_id=data.team_id,
            address_id=data.address_id,
            specie_id=data.specie_id,
            ideogram_id=data.ideogram_id,
            folder_id=data.folder_id,
            kariotype_id=data.kariotype_id,
            actived=data.actived,
            revoked=data.revoked,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        ).to_mongo().to_dict()

        result = await self.collection.insert_one(invitation_data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return await self.get_by_id(str(model["_id"]))

    async def delete(self, id: str):
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    async def get_by_id(self, id: str):
        return await self.collection.find_one({"_id": id, "revoked": False})

    async def get_by_email(self, email: str):
        return await self.collection.find_one({"email": email, "revoked": False})

    async def get_by_owner_user_id(self, owner_user_id: str, team_id: str):
        cursor = self.collection.find({"owner_user_id": owner_user_id, "team_id": team_id, "revoked": False})\
                                .sort("modified_at", DESCENDING)
        return await cursor.to_list(length=None)
    
    async def get_by_guest_user_id(self, guest_user_id: str, team_id: str):
        return await self.collection.find_one({"guest_user_id": guest_user_id, "team_id": team_id, "revoked": False}) 

    async def get_active_invitations(self, team_id: str = None):
        query = {"actived": True, "revoked": False}
        if team_id:
            query["team_id"] = team_id
        cursor = self.collection.find(query).sort("modified_at", DESCENDING)
        return await cursor.to_list(length=None)

    async def get_invite(self, owner_user_id: str, team_id: str, email: str, item_id: str):
        query = {
            "owner_user_id": owner_user_id,
            "team_id": team_id,
            "email": email,
            "revoked": False,
            "$or": [
                {"address_id": item_id},
                {"specie_id": item_id},
                {"ideogram_id": item_id},
                {"folder_id": item_id},
                {"volunteer_id": item_id},
                {"kariotype_id": item_id}
            ]
        }

        return await self.collection.find_one(query)

    async def get_by_user_or_team(
        self,
        order_by: str = "-created_at",
        search: str = "",
        team_id: str = None,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10
    ):
        query = {
            "revoked": False
        }
        query_grant = {
            "revoked": False,
        }
        query['$or'] = [
            {'owner_user_id': user_id},
            {"guest_user_id": user_id}
        ]

        if team_id:
            query['team_id'] = team_id
            query_grant['team_id'] = team_id
   
        if search:
            query['$and'] = [
                {"$or": [
                    {"user_id": user_id},
                    {"guest_user_id": user_id}
                ]},
                {"$or": [
                    {"email": {"$regex": search, "$options": "i"}},
                ]}
            ]

        grants_by_invitation_id = {}
        accessible_invitation_ids = []
       
        query_grant['$or'] = [
            {'owner_user_id': user_id},
            {"guest_user_id": user_id}
        ]
        grants_cursor = self.collection_grants.find(query_grant)

        async for grant in grants_cursor:
            invitation_id = grant["invitation_id"]
            accessible_invitation_ids.append(invitation_id)
            grants_by_invitation_id[invitation_id] = {
                "roles": grant.get("roles"),
                "rules": grant.get("rules")
            }
    
        total_folders = await self.collection.count_documents(query)
  
        if order_by is None:
            order_by = "-created_at"

        sort_order = DESCENDING if order_by.startswith("-") else 1
        sort_field = order_by.lstrip("-")

        cursor = self.collection.find(query)\
                                .sort(sort_field, sort_order)\
                                .skip((page - 1) * page_size)\
                                .limit(page_size)

        list_ = []
        async for data in cursor:
            invitation_data = {**data, "id": str(data["_id"])}

            if data["_id"] in accessible_invitation_ids:
                invitation_data.update(grants_by_invitation_id[data["_id"]])
            else:
                invitation_data.update({
                    "roles": [role.value for role in RolesEnum],
                    "rules": [rule.value for rule in RulesEnum]
                })
            list_.append(invitation_data)

        return {
            "total": total_folders,
            "page": page,
            "page_size": page_size,
            "invitations": list_
        }
