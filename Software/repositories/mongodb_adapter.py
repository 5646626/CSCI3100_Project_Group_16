from config import get_database
from pymongo.errors import PyMongoError

#-----------------MongoDB Adapter-----------------#
class MongoDBAdapter: 
    def __init__(self):
        self.db = get_database()

    # Insert a single document
    def insert_one(self, collection_name: str, document: dict):
        try:
            collection = self.db[collection_name]       # Get the collection
            result = collection.insert_one(document)    # Insert the document
            return result.inserted_id                   # Return the inserted document ID
        except PyMongoError as e:
            raise Exception(f"MongoDB insert error: {e}")
    
    # Find and return a single document
    def find_one(self, collection_name: str, query: dict):  # query e.g. {"username": "testuser"}
        try:
            collection = self.db[collection_name]
            return collection.find_one(query)
        except PyMongoError as e:
            raise Exception(f"MongoDB find error: {e}")
    
    # Find multiple documents
    # Returns a list of documents matching the query
    # limit specifies the maximum number of documents to return
    # Example: adapter.find_many("tasks", {"status": "todo"}, limit=10) means find up to 10 tasks with status "todo"
    def find_many(self, collection_name: str, query: dict = None, limit: int = 0):
        try:
            collection = self.db[collection_name]       # Get the collection
            query = query or {}
            return list(collection.find(query).limit(limit if limit > 0 else 0))
        except PyMongoError as e:
            raise Exception(f"MongoDB find error: {e}")

    # Update a single document
    # Can update multiple fields, e.g.
    # adapter.update_one(
    #   "tasks", 
    #   {"_id": 5}, 
    #   {
    #       "status": "done",
    #       "priority": "high",
    #       "updated_at": "2025-12-20"
    #   }
    # )
    def update_one(self, collection_name: str, query: dict, update: dict):
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": update})
            return result.modified_count
        except PyMongoError as e:
            raise Exception(f"MongoDB update error: {e}")
    
    # Delete a single document
    def delete_one(self, collection_name: str, query: dict):
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            return result.deleted_count
        except PyMongoError as e:
            raise Exception(f"MongoDB delete error: {e}")
    
    # Create an index on a field
    # It helps to speed up queries on that field
    # Example: adapter.create_index("users", "username")
    def create_index(self, collection_name: str, field: str, unique: bool = False):
        try:
            collection = self.db[collection_name]
            collection.create_index(field, unique=unique)
        except PyMongoError as e:
            msg = str(e)
            # Ignore benign conflicts when an index already exists with different options
            if "already exists" in msg or "IndexOptionsConflict" in msg:
                return
            raise Exception(f"MongoDB index error: {e}")