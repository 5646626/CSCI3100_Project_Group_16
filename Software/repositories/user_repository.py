from models.base_user import Members, Hashira, Boss
from repositories.mongodb_adapter import MongoDBAdapter
from bson import ObjectId
import hashlib

#---------------User Repository-----------------#
class UserRepository:

    COLLECTION_NAME = "users"

    def __init__(self, adapter: MongoDBAdapter = None):
        self.adapter = adapter or MongoDBAdapter()
    
    def create_new_user(self, user: Members) -> ObjectId:
        doc = user.to_dict()
        user_id = self.adapter.insert_one(self.COLLECTION_NAME, doc)
        return user_id

    def find_user_by_username(self, username: str) -> Members:
        doc = self.adapter.find_one(self.COLLECTION_NAME, {"username": username})
        if not doc:
            return None
        return self._instantiate_user(doc)
    
    def find_user_by_id(self, user_id: ObjectId) -> Members:
        doc = self.adapter.find_one(self.COLLECTION_NAME, {"_id": user_id})
        if not doc:
            return None
        return self._instantiate_user(doc)
    
    # Find all users with a specific role, returns a list of user objects
    def find_user_by_role(self, role: str) -> list:
        docs = self.adapter.find_many(self.COLLECTION_NAME, {"role": role})
        return [self._instantiate_user(doc) for doc in docs]
    
    # Not used currently, used by update_user_role
    def update_user_field(self, user_id: ObjectId, updates: dict) -> bool:
        modified = self.adapter.update_one(
            self.COLLECTION_NAME,
            {"_id": user_id},
            updates
        )
        return modified > 0 # Return True if at least one document was modified
    
    # Not used currently, but useful for changing user roles in the future
    def update_user_role(self, user_id: ObjectId, new_role: str) -> bool:
        valid_roles = ["Members", "Hashira", "Boss"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        return self.update_user_field(user_id, {"role": new_role})
    
    #---------------Helper Functions-----------------#
    # Hash password using SHA-256
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Factory method to instantiate correct user class based on role
    @staticmethod
    def _instantiate_user(doc: dict) -> Members:
        role = doc.get("role", "Members")  # Default to Members if role not found
        common_kwargs = {
            "username": doc.get("username"),
            "password_hash": doc.get("password_hash"),
            "email": doc.get("email"),
            "_id": doc.get("_id"),
        }

        if role == "Boss":
            return Boss(**common_kwargs)
        elif role == "Hashira":
            return Hashira(**common_kwargs)
        else:  # Default to Members
            return Members(**common_kwargs)