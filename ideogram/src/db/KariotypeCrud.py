import datetime
from typing import List
from pymongo import DESCENDING
from ..models.KariotypeModel import KariotypeModel, Chromosome


class KariotypeRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db['kariotypes']

    def create(self, data):
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
            empty=data.empty,
            batches_total=data.batches_total,
            address_id=data.address_id,
            scheduled=data.scheduled or datetime.datetime.utcnow(),
            specie_id=data.specie_id,
            folder_id=data.folder_id,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow()
        ).to_mongo().to_dict()

        result = self.collection.insert_one(kariotype_data)
        return self.get_by_id(str(result.inserted_id))

    def update(self, model: dict, data: dict):
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['modified_at'] = datetime.datetime.utcnow()

        self.collection.update_one(
            {"_id": model["_id"]},
            {"$set": update_data}
        )
        return self.get_by_id(str(model["_id"]))

    def bulk_update(self, parent_id: str, update_fields: List[dict]):
        """
        Updates specific chromosomes in a document based on the `id` and fields to update.

        :param parent_id: The ID of the parent document containing the chromosomes array.
        :param update_fields: List of dictionaries containing `id` of the chromosome and fields to update.
        :return: None
        """
        updated = None
        for update in update_fields:
            chromosome_id = update.get("id_chromosome")

            current_time = datetime.datetime.utcnow()
            update["modified_at"] = current_time 

            query = {}
            for key, value in update.items():
                query[f"chromosomes.$.{key}"] = value
        
            updated = self.collection.update_one(
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

    def delete(self, id: str):
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count == 1
    
    def bulk_remove(self, parent_id: str, chroms_ids: List[dict]):
        """
        Removes specific chromosomes from a document based on the `id` of the chromosome.

        :param parent_id: The ID of the parent document containing the chromosomes array.
        :param remove_fields: List of dictionaries containing the `id` of the chromosomes to remove.
        :return: Result of the last removal operation.
        """
        removed = None
        for chromosome_id in chroms_ids:

            removed = self.collection.update_one(
                {
                    "_id": parent_id
                },
                {
                    "$pull": {
                        "chromosomes": {
                            "id_chromosome": chromosome_id
                        }
                    }
                }
            )

        return removed

    def get_by_id(self, id: str):
        query = {"_id": id}
        return self.collection.find_one(query)
 