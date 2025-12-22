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

    def find_board_by_id(self, board_id: ObjectId) -> Board:
        doc = self.adapter.find_one(self.COLLECTION_NAME, {"_id": board_id})
        if not doc:
            return None
        return Board(**{**doc, '_id': doc['_id']})
    
    def find_board_by_owner(self, owner_id: ObjectId) -> list:
        docs = self.adapter.find_many(self.COLLECTION_NAME, {"owner_id": owner_id})
        return [Board(**{**doc, '_id': doc['_id']}) for doc in docs]
    
    # Find board by name but also match owner_id to ensure uniqueness per user
    def find_board_by_name(self, name: str, owner_id: ObjectId) -> Board:
        doc = self.adapter.find_one(
            self.COLLECTION_NAME,
            {"name": name, "owner_id": owner_id}
        )
        if not doc:
            return None
        return Board(**{**doc, '_id': doc['_id']})
    
    # Find all boards matching a given name, regardless of owner
    def find_boards_by_name(self, name: str) -> list:
        docs = self.adapter.find_many(self.COLLECTION_NAME, {"name": name})
        return [Board(**{**doc, '_id': doc['_id']}) for doc in docs]
    
    def delete_board(self, board_id: ObjectId) -> bool:
        deleted = self.adapter.delete_one(
            self.COLLECTION_NAME,
            {"_id": board_id}
        )
        return deleted > 0

#----------Not currenly used, but could implemented in the future----------#
#   Adding update/delete board features
#    def update_board(self, board_id: ObjectId, updates: dict) -> bool:
#        modified = self.adapter.update_one(
#            self.COLLECTION_NAME,
#            {"_id": board_id},
#            updates
#        )
#        return modified > 0