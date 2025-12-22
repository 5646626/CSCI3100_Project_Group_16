from models.entities import Licence
from repositories.mongodb_adapter import MongoDBAdapter
from bson import ObjectId

#----------------Licence Repository-----------------#
class LicenceRepository:
    
    COLLECTION_NAME = "licences"
    
    def __init__(self, adapter: MongoDBAdapter = None):
        self.adapter = adapter or MongoDBAdapter()
        self.adapter.create_index(self.COLLECTION_NAME, "key", unique=True)
        self.adapter.create_index(self.COLLECTION_NAME, "owner_id")
        self.adapter.create_index(self.COLLECTION_NAME, "role")
    
    def create_licence(self, licence: Licence) -> ObjectId:
        doc = licence.to_dict()
        licence_id = self.adapter.insert_one(self.COLLECTION_NAME, doc)
        return licence_id
    
    def find_licence_by_key(self, key: str) -> Licence:
        doc = self.adapter.find_one(self.COLLECTION_NAME, {"key": key})
        if not doc:
            return None
        return Licence(**{**doc, '_id': doc['_id']})

    def assign_owner(self, key: str, owner_id: ObjectId) -> bool:
        """Bind a licence key to a user if it is not already claimed."""
        modified = self.adapter.update_one(
            self.COLLECTION_NAME,
            {"key": key, "owner_id": None},
            {"owner_id": owner_id},
        )
        return modified > 0
    
    # Validate if a licence key exists
    def validate_licence(self, key: str) -> bool:
        return self.find_licence_by_key(key) is not None

#-----------Not currenly used, but could implemented in the future----------#
#   Finding licences owned by a user
#    def find_licence_by_owner(self, owner_id: ObjectId) -> Licence:
#        doc = self.adapter.find_one(self.COLLECTION_NAME, {"owner_id": owner_id})
#        if not doc:
#            return None
#        return Licence(**{**doc, '_id': doc['_id']})