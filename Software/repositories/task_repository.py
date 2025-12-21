from models.entities import Task
from repositories.mongodb_adapter import MongoDBAdapter
from bson import ObjectId

#----------------Task Repository-----------------#
class TaskRepository:
    
    COLLECTION_NAME = "tasks"
    
    def __init__(self, adapter: MongoDBAdapter = None):
        self.adapter = adapter or MongoDBAdapter()
        self.adapter.create_index(self.COLLECTION_NAME, "board_id")
        self.adapter.create_index(self.COLLECTION_NAME, "assigned_to")
    
    def create_task(self, task: Task) -> ObjectId:
        doc = task.to_dict()
        task_id = self.adapter.insert_one(self.COLLECTION_NAME, doc)
        return task_id

    def create(self, task: Task) -> ObjectId:
        return self.create_task(task)
    
    def find_task_by_id(self, task_id: ObjectId) -> Task:
        doc = self.adapter.find_one(self.COLLECTION_NAME, {"_id": task_id})
        if not doc:
            return None
        return Task(**{**doc, '_id': doc['_id']})

    def find_by_id(self, task_id: ObjectId) -> Task:
        return self.find_task_by_id(task_id)
    
    def find_task_by_board(self, board_id: ObjectId) -> list:
        docs = self.adapter.find_many(self.COLLECTION_NAME, {"board_id": board_id})
        return [Task(**{**doc, '_id': doc['_id']}) for doc in docs]

    def find_by_board(self, board_id: ObjectId) -> list:
        return self.find_task_by_board(board_id)
    
    def find_task_by_column(self, board_id: ObjectId, column: str) -> list:
        docs = self.adapter.find_many(
            self.COLLECTION_NAME,
            {"board_id": board_id, "column": column}
        )
        return [Task(**{**doc, '_id': doc['_id']}) for doc in docs]

    def find_by_column(self, board_id: ObjectId, column: str) -> list:
        return self.find_task_by_column(board_id, column)
    
    def update_task(self, task_id: ObjectId, updates: dict) -> bool:
        modified = self.adapter.update_one(
            self.COLLECTION_NAME,
            {"_id": task_id},
            updates
        )
        return modified > 0

    def update(self, task_id: ObjectId, updates: dict) -> bool:
        return self.update_task(task_id, updates)
    
    def delete_task(self, task_id: ObjectId) -> bool:
        deleted = self.adapter.delete_one(
            self.COLLECTION_NAME,
            {"_id": task_id}
        )
        return deleted > 0

    def delete(self, task_id: ObjectId) -> bool:
        return self.delete_task(task_id)
    
    def search_task(self, board_id: ObjectId, keyword: str) -> list:
        docs = self.adapter.find_many(
            self.COLLECTION_NAME,
            {
                "board_id": board_id,
                "$or": [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}}
                ]
            }
        )
        return [Task(**{**doc, '_id': doc['_id']}) for doc in docs]

    def search(self, board_id: ObjectId, keyword: str) -> list:
        return self.search_task(board_id, keyword)