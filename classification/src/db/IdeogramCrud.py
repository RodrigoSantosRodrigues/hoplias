import datetime
from pymongo import DESCENDING
from ..models.IdeogramModel import IdeogramModel


class IdeogramRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db['ideograms']

    def create(self, data):
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

        result = self.collection.insert_one(ideogram_data)
        return self.get_by_id(str(result.inserted_id))

    def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.datetime.utcnow()

        self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return self.get_by_id(str(model["_id"]))

    def delete(self, id: str):
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    def get_by_id(self, id: str):
        query = {"_id": id}
        return self.collection.find_one(query)
