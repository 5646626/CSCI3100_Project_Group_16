from models.entities import Board
from repositories.mongodb_adapter import MongoDBAdapter
from bson import ObjectId

#----------------Board Repository-----------------#
class BoardRepository:
    
    COLLECTION_NAME = "boards"
    
    def __init__(self, adapter: MongoDBAdapter = None):
        self.adapter = adapter or MongoDBAdapter()
        self.adapter.create_index(self.COLLECTION_NAME, "owner_id")
        self.adapter.create_index(self.COLLECTION_NAME, "name")
    
    def create_board(self, board: Board) -> ObjectId:
        doc = board.to_dict()
        board_id = self.adapter.insert_one(self.COLLECTION_NAME, doc)
        return board_id

    # Shorthand to match service expectations
    def create(self, board: Board) -> ObjectId:
        return self.create_board(board)
    
    def find_board_by_id(self, board_id: ObjectId) -> Board:
        doc = self.adapter.find_one(self.COLLECTION_NAME, {"_id": board_id})
        if not doc:
            return None
        return Board(**{**doc, '_id': doc['_id']})

    def find_by_id(self, board_id: ObjectId) -> Board:
        return self.find_board_by_id(board_id)
    
    def find_board_by_owner(self, owner_id: ObjectId) -> list:
        docs = self.adapter.find_many(self.COLLECTION_NAME, {"owner_id": owner_id})
        return [Board(**{**doc, '_id': doc['_id']}) for doc in docs]

    def find_by_owner(self, owner_id: ObjectId) -> list:
        return self.find_board_by_owner(owner_id)
    
    # Find board by name but also match owner_id to ensure uniqueness per user
    def find_board_by_name(self, name: str, owner_id: ObjectId) -> Board:
        doc = self.adapter.find_one(
            self.COLLECTION_NAME,
            {"name": name, "owner_id": owner_id}
        )
        if not doc:
            return None
        return Board(**{**doc, '_id': doc['_id']})

    def find_by_name(self, name: str, owner_id: ObjectId) -> Board:
        return self.find_board_by_name(name, owner_id)
    
    def update_board(self, board_id: ObjectId, updates: dict) -> bool:
        modified = self.adapter.update_one(
            self.COLLECTION_NAME,
            {"_id": board_id},
            updates
        )
        return modified > 0

    def update(self, board_id: ObjectId, updates: dict) -> bool:
        return self.update_board(board_id, updates)
    
    def delete_board(self, board_id: ObjectId) -> bool:
        deleted = self.adapter.delete_one(
            self.COLLECTION_NAME,
            {"_id": board_id}
        )
        return deleted > 0

    def delete(self, board_id: ObjectId) -> bool:
        return self.delete_board(board_id)